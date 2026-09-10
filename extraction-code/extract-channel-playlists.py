"""Extract /playlists + /courses per channel -> two JSONL files. Resume-safe via id dedup."""
import json
import sys
from pathlib import Path

import yt_dlp

PARENT_DIR = Path(__file__).parent
INPUT_FILE = PARENT_DIR / "input" / "sub-channels.txt"
OUTPUT_DIR = PARENT_DIR / "output"
PLAYLISTS_OUT = OUTPUT_DIR / "channel-playlists.jsonl"
COURSES_OUT = OUTPUT_DIR / "channel-courses.jsonl"


def load_seen(path):
    seen = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    seen.add(json.loads(line)["id"])
                except (KeyError, ValueError):
                    continue
    return seen


def fetch_tab(ydl, channel_id, tab):
    url = f"https://www.youtube.com/channel/{channel_id}/{tab}"
    try:
        info = ydl.extract_info(url, download=False)
        if not info or not info.get("entries"):
            return []
        out = []
        for e in info["entries"]:  # iterate inside try: page-2 fetch can raise mid-loop
            if e and e.get("id"):
                out.append({
                    "id": e["id"],
                    "title": e.get("title", ""),
                    "url": e.get("url") or f"https://www.youtube.com/playlist?list={e['id']}",
                    "channel_id": channel_id,
                    "type": "course" if tab == "courses" else "playlist",
                })
        return out
    except Exception as e:  # ponytail: broad catch, one bad channel must not kill 491-channel run
        print(f"skip {channel_id}/{tab}: {e}")
        return []


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    channels = [l.strip() for l in INPUT_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
    if limit:
        channels = channels[:limit]
    OUTPUT_DIR.mkdir(exist_ok=True)
    seen_pl, seen_co = load_seen(PLAYLISTS_OUT), load_seen(COURSES_OUT)
    ydl_opts = {"skip_download": True, "extract_flat": True, "quiet": True, "no_warnings": True, "ignoreerrors": True}
    n_pl = n_co = 0
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for cid in channels:
            try:
                for item in fetch_tab(ydl, cid, "playlists"):
                    if item["id"] not in seen_pl:
                        seen_pl.add(item["id"])
                        with open(PLAYLISTS_OUT, "a", encoding="utf-8") as f:
                            f.write(json.dumps(item, ensure_ascii=False) + "\n")
                        n_pl += 1
                for item in fetch_tab(ydl, cid, "courses"):
                    if item["id"] not in seen_co:
                        seen_co.add(item["id"])
                        with open(COURSES_OUT, "a", encoding="utf-8") as f:
                            f.write(json.dumps(item, ensure_ascii=False) + "\n")
                        n_co += 1
                print(f"{cid}: +{n_pl} playlists, +{n_co} courses (running totals this run)", flush=True)
            except Exception as e:
                print(f"skip {cid}: {e}", flush=True)
                continue
    print(f"done: +{n_pl} playlists, +{n_co} courses")


if __name__ == "__main__":
    main()
