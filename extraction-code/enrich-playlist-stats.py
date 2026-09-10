"""Enrich channel-playlists/courses JSONL with totals. Resume-safe: skips enriched entries.

One cheap flat fetch per playlist yields everything: video durations sum,
video count, and the playlist page's own view count ("3,610 views" header).
"""
import json
import sys
import time
from pathlib import Path

import yt_dlp

PARENT_DIR = Path(__file__).parent
OUTPUT_DIR = PARENT_DIR / "output"
TARGETS = [OUTPUT_DIR / "channel-playlists.jsonl", OUTPUT_DIR / "channel-courses.jsonl"]

FLAT_OPTS = {"skip_download": True, "extract_flat": True, "quiet": True, "no_warnings": True, "ignoreerrors": True}


def fmt(secs):
    h, m, s = secs // 3600, (secs % 3600) // 60, secs % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def load(path):
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def save(path, records):
    tmp = path.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")
    tmp.replace(path)


def enrich(ydl, rec):
    info = ydl.extract_info(f"https://www.youtube.com/playlist?list={rec['id']}", download=False)
    entries = [e for e in (info.get("entries") or []) if e and e.get("id")]
    secs = sum(int(e["duration"]) for e in entries if e.get("duration"))
    rec["total_duration_seconds"] = secs
    rec["total_duration_text"] = fmt(secs)
    rec["video_count"] = len(entries)
    rec["playlist_views"] = info.get("view_count")  # playlist page's own "N views", not summed videos
    rec.pop("total_views", None)  # drop stale summed-video-views from earlier probe runs


def backfill(ydl, rec):
    info = ydl.extract_info(f"https://www.youtube.com/playlist?list={rec['id']}", download=False)
    thumbs = info.get("thumbnails") or []
    if thumbs:
        rec["thumbnail_url"] = thumbs[-1].get("url") or thumbs[0].get("url")
    rec["channel_name"] = info.get("channel") or info.get("uploader") or ""


def main():
    args = sys.argv[1:]
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
    sleep = float(args[args.index("--sleep") + 1]) if "--sleep" in args else 1.0
    mode = args[args.index("--mode") + 1] if "--mode" in args else "enrich"
    fn, key = (backfill, "thumbnail_url") if mode == "backfill" else (enrich, "playlist_views")

    for path in TARGETS:
        records = load(path)
        todo = [r for r in records if key not in r]
        if limit:
            todo = todo[:limit]
        print(f"{path.name}: {len(todo)} to {mode}", flush=True)
        done = 0
        with yt_dlp.YoutubeDL(FLAT_OPTS) as ydl:
            for rec in todo:
                try:
                    fn(ydl, rec)
                    done += 1
                    if done % 25 == 0:
                        save(path, records)
                        print(f"  checkpoint {done}/{len(todo)}", flush=True)
                except Exception as e:  # ponytail: one bad playlist must not kill a 7793-playlist run
                    print(f"  skip {rec['id']}: {e}", flush=True)
                time.sleep(sleep)
        save(path, records)
        print(f"{path.name}: +{done} enriched", flush=True)


if __name__ == "__main__":
    main()
