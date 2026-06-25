import scrapy


class ytSSF_Spider(scrapy.Spider):
    name = "yt-ssf"
    start_urls = []
    base_url = "https://www.youtube.com/watch?v="
    with open("./input/subs_feed_video_ids.txt", "r", encoding="utf-16") as in_file:
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
