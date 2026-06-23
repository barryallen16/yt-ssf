import yt_dlp
import json
from tqdm import tqdm
from yt_dlp.utils import DownloadError


def extract_vid_info():

    OUT_FILENAME = "extract.jsonl"
    video_ids = []
    already_processed_videoids = set()

    with open("./extract.jsonl", "r", encoding="utf-8") as in_file:
        for line in in_file:
            if line.strip() and line.strip() not in already_processed_videoids:
                data = json.loads(line)
                video_id = data["id"]
                already_processed_videoids.add(video_id)
    print(f"Found {len(already_processed_videoids)} already processed videoids")

    with open("./subs_feed_video_ids.txt", "r", encoding="utf-16") as in_file:
        for line in in_file:
            if line.strip() and line.strip() not in already_processed_videoids:
                video_ids.append(line.strip())

    print(f"Processing {len(video_ids)} unprocessed video_ids")
    ydl_opts = {"extract_flat": True, "ignore_warnings": True, "skip-download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for video_id in tqdm(video_ids, desc="Processing video id", unit="video"):
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
                with open(OUT_FILENAME, "a", encoding="utf-8") as out_file:
                    json.dump(result_dict, out_file, ensure_ascii=False)
                    out_file.write("\n")
            except DownloadError:
                tqdm.write(f"download error on video id {video_id}. skipping..")
                video_ids.remove(video_id)
                continue
    print(f"Processed {len(video_ids)} video_ids and written results to {OUT_FILENAME}")


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
