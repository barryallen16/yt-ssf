import yt_dlp
import json
from tqdm import tqdm
from yt_dlp.utils import DownloadError, ExtractorError
import time


class IgnoreLogger:
    def error(msg):
        pass

    def warning(msg):
        pass

    def debug(msg):
        pass


def extract_vid_info():

    OUT_FILEPATH = "./output/extract.jsonl"
    VIDEOIDS_FILEPATH = "./input/subs_feed_video_ids.txt"
    video_ids = []
    already_processed_videoids = set()
    always_skip_video_ids = set()

    try:
        with open(
            "./input/always_skip_video_ids.txt", "r", encoding="utf-8"
        ) as out_file:
            for line in out_file:
                if line.strip():
                    always_skip_video_ids.add(line.strip())
    except FileNotFoundError:
        pass
    print(f"Found {len(always_skip_video_ids)} video ids to always skip")
    try:
        with open(OUT_FILEPATH, "r", encoding="utf-8") as in_file:
            for line in in_file:
                if line.strip():
                    data = json.loads(line)
                    video_id = data["id"]
                    already_processed_videoids.add(video_id)
    except FileNotFoundError:
        pass

    print(f"Found {len(already_processed_videoids)} already processed videoids")

    with open(VIDEOIDS_FILEPATH, "r", encoding="utf-16") as in_file:
        for line in in_file:
            if (
                line.strip()
                and line.strip() not in already_processed_videoids
                and line.strip() not in always_skip_video_ids
            ):
                video_ids.append(line.strip())

    print(f"Processing {len(video_ids)} unprocessed video_ids")
    ydl_opts = {
        "extract_flat": True,
        "no_warnings": True,
        "skip_download": True,
        "quiet": True,
        "logger": IgnoreLogger,
    }
    success_count = 0
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for video_id in tqdm(video_ids, desc="Processing video id", unit="video"):
            time.sleep(5)

            try:
                info = ydl.extract_info(
                    url=f"https://youtube.com/watch?v={video_id}", download=False
                )
                result_dict = {
                    "id": info.get("id", ""),
                    "title": info.get("title", ""),
                    "uploader": info.get("uploader", ""),
                    "description": info.get("description", ""),
                }
                with open(OUT_FILEPATH, "a", encoding="utf-8") as out_file:
                    json.dump(result_dict, out_file, ensure_ascii=False)
                    out_file.write("\n")
                success_count += 1
            except (DownloadError, ExtractorError, Exception) as e:
                if (
                    any(
                        keyword in str(e)
                        for keyword in ["removed", "confirm your age", "not available"]
                    )
                ) and video_id not in always_skip_video_ids:
                    with open(
                        "./input/always_skip_video_ids.txt", "a", encoding="utf-8"
                    ) as out_file:
                        out_file.write(video_id + "\n")
                tqdm.write(f"download error on video id {video_id} - {str(e)}")
                continue

    print(f"Processed {success_count} video_ids and written results to {OUT_FILEPATH}")


banner = """
██╗   ██╗████████╗   ███████╗███████╗███████╗
╚██╗ ██╔╝╚══██╔══╝   ██╔════╝██╔════╝██╔════╝
 ╚████╔╝    ██║█████╗███████╗███████╗█████╗  
  ╚██╔╝     ██║╚════╝╚════██║╚════██║██╔══╝  
   ██║      ██║      ███████║███████║██║     
   ╚═╝      ╚═╝      ╚══════╝╚══════╝╚═╝     
    (youtube search subscription feed)                                    
"""
if __name__ == "__main__":
    print(banner)
    extract_vid_info()
