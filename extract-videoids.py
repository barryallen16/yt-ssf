import yt_dlp


def extract_subfeed_videoids():

    ydl_opts = {
        "skip-download": True,
        "extract_flat": True,
        "cookiefile": "yt-cookie.txt",
        "quiet": True,
        "no_warnings": True,
    }
    url = "https://www.youtube.com/feed/subscriptions"
    print("Fetching video ids from subscription feed..")
    video_ids = set()
    with yt_dlp.YoutubeDL() as ydl:
        extract = ydl.extract_info(url, download=False)
        if "entries" in extract:
            for entry in extract["entries"]:
                if entry and "id" in entry:
                    video_ids.add(entry["id"])
    print(f"Extracted {len(video_ids)} video ids from subscription feed.")
    out_filename = "subfeed_videoids.txt"
    with open(out_filename, "w", encoding="utf-8") as out_file:
        for vid in video_ids:
            out_file.write(vid + "\n")
    print(f"Finished writing video_ids to {out_filename}")


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
    extract_subfeed_videoids()
