import scrapy
from pathlib import Path
PARENT_DIR = Path(__file__).parent
INPUT_DIR = PARENT_DIR / "input"

PROCESS_UNPROCESSED = False

INPUT_FILE_PATH = INPUT_DIR / "unprocessed_vidx.txt" if PROCESS_UNPROCESSED else INPUT_DIR / "subs_feed_video_ids.txt"

class ytSSF_Spider(scrapy.Spider):
    name = "yt-ssf"
    start_urls = []
    base_url = "https://www.youtube.com/watch?v="
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as in_file:
        for line in in_file:
            if line.strip():
                video_url = base_url + line.strip()
                start_urls.append(video_url)

    def parse(self, response):
        video_id = response.request.url.replace("https://www.youtube.com/watch?v=", "")
        thumbnail_url = (
            "https://i.ytimg.com/vi/" + video_id + "/hqdefault.jpg"
        )  # low resolution thumbnail
        maxres_thumbnail_url = (
            "https://i.ytimg.com/vi/" + video_id + "/maxresdefault.jpg"
        )  # high resolution thumbnail
        yield {
            "id": video_id,
            "thumbnail_url": thumbnail_url,
            "maxres_thumbnail_url": maxres_thumbnail_url,
            "title": response.css("meta[name='title']::attr(content)").get(),
            "channel_name": response.css("link[itemprop='name']::attr(content)").get(),
            "description": response.css(
                "meta[name='description']::attr(content)"
            ).get(),
        }
