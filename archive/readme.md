### YT-SSF
![alt text](static/terminal.png)                    
yt-ssf (youtube Search Subscription Feed) can be used to search through your subscription feed for specific keyword.
it uses yt-dlp to extract all the video_ids from your `https://youtube.com/subscription/feed`. but since your subscription feed is private to you, you need to pass yt cookie to get all the video ids in your subscription feed. after retrieving the video ids, you can extract the videos id info with or without cookie. 
- without cookie, 300 videos info can be extracted / hour. (ie yt sees you as a guest user)
- with cookie, 2000 videos info can be extracted / hour.

## Why extract the video info?
By extracting the video info such as : title, description, uploader(channel name) along with the video id , We can build a lighting fast searchable self hosted database via meilisearch. 
We store the results to a ndjson or jsonlines file, as it is easier to validate and requires less computation.

## Steps:

1. Go to extension web store in whatever browser you are using youtube in. 
2. Search for `Get cookies.txt LOCALLY` extension and install it.

![alt text](static/image.png) 

3. Go to `youtube.com` and click on the `Get cookies.txt LOCALLY` extension

![alt text](static/image-1.png)

4. click `export` button to export the yt cookie in netscape format. (Keep in mind, so share this netscape format cookie to anyone. or else they could use your yt account until unless you explicitly logged out and the cookie expires.)
5. Save the cookie as `youtube-netscape-cookie.txt` or whatever you prefer and place it in the `extraction-code/input` directory.
6. replace the filename in `extraction-code/extract-videoids.py` with what you saved your cookie file as.
```code
COOKIE_FILEPATH ="./input/youtube-netscape-cookie.txt"
```
7. run `python3 extraction-code/extract-videoids.py`, which will extract all the video ids in your subscription feed and stores it in `extracted-code/input/subs_feed_video_ids.txt`
8. run `python3 extraction-code/scrapy-implementation.py`, which will extract all the info of the video ids so that we can build a searchable database with it.
9. setup meilisearch and launch meilisearch in the devices you are going to use(vps or local) 
```
# Install Meilisearch
curl -L https://install.meilisearch.com | sh
# Launch Meilisearch
#replace `barryallen@16` with your preferred masterkey .
./meilisearch --master-key="barryallen@16"
```
10. Then from the system having the repo, replace `MEILISEARCH_URL` with the actual url and run 
```
cd extraction-code\output
curl ^
  -X POST "MEILISEARCH_URL/indexes/yt-ssf/documents?primaryKey=id" ^
  -H "Content-Type: application/x-ndjson" ^
  -H "Authorization: Bearer barryallen@16" ^
  --data-binary @scrapy-extract.jsonl
curl ^
  -X GET "MEILISEARCH_URL/tasks/0" ^
  -H "Authorization: Bearer barryallen@16"
```
also rememeber to replace the meilisearch url enpoint in the index.html. then host the website and search for what you need in subscription feed at lighting speed.

## Lesson
- i first used `yt-dlp` library to scarpe the video infos such as thumbnail, title, channel name, video description. but this was too slow; rate limiting allowed only 300 videos to be scrape per day. that too, i would have to wait 5 secs per video so that i don't get banned.it would take almost 58 days to scrape my 17,599 sub feed videos, considering the 300 video rate limit/per. making this method infeasible.
- then i implemented the logic in `scrapy` library, and it took 40 mins to completely scrape my 17,599 sub feed videos.