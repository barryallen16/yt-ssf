### YT-SSF
![alt text](static/web-image.png)                   
yt-ssf (youtube Search Subscription Feed) can be used to search through your subscription feed for specific keyword.
it uses yt-dlp to extract all the video_ids from your `https://youtube.com/subscription/feed`. but since your subscription feed is private to you, you need to pass yt cookie to get all the video ids in your subscription feed. after retrieving the video ids, you can extract the videos id info (such as title, description, channel name, thumbnail_url) using `scrapy` library.
you can demo this at [link](https://barryallen16.github.io/yt-ssf/) which searches through my subscription feed videos

## Why extract the video info?
By extracting the video info such as : title, description, channel name, thumbnail_url along with the video id , We can build a lighting fast searchable self hosted database via meilisearch. 
We store the results to a ndjson or jsonlines file, as it is easier to validate and requires less computation.

## Quickstart
1. download and install `yt-dlp` specific to your platform from [github](https://github.com/yt-dlp/yt-dlp#installation)
2. After installing, run 
```bash
git clone https://github.com/barryallen16/yt-ssf
cd yt-ssf
```
3. Go to extension web store in whatever browser you are using youtube in. 
4. Search for `Get cookies.txt LOCALLY` extension and install it.

![alt text](static/image.png) 

5. Go to `youtube.com` and click on the `Get cookies.txt LOCALLY` extension

![alt text](static/image-1.png)

6. click `export` button to export the yt cookie in netscape format. (Keep in mind, so share this netscape format cookie to anyone. or else they could use your yt account until unless you explicitly logged out and the cookie expires.)
7. Save the cookie as `youtube-netscape-cookie.txt` or whatever you prefer and place it in the `extraction-code/input` directory.
8. activate virtual env, run to install requirements and clear my video_ids and video_ids extract jsonl file  
```
pip install -r extraction-code/requirements.txt
python3 extraction-code/start-fresh.py
```
8. then replace `youtube-netscape-cookie.txt` with cookie file name you saved it as and run. 
remove -v argument if you dont want to see progress.
```bash
yt-dlp -v --cookies extraction-code/input/youtube-netscape-cookie.txt --flat-playlist --print id "https://www.youtube.com/feed/subscriptions" > extraction-code/input/subs_feed_video_ids.txt
```
9. activate virtual env, install requirements and run scarpy spider script 
```
pip install -r extraction-code/requirements.txt
scrapy runspider scarpy-implementation.py -o ./extraction-code/output/scrapy-extract.jsonl
```
10. setup meilisearch and launch meilisearch in the devices you are going to use(vps or local) 
```
# Install Meilisearch
curl -L https://install.meilisearch.com | sh
# Launch Meilisearch
# install tmux and start a new session
sudo apt update 
sudo apt install -y tmux
tmux new -s meilisearch-session
tmux attach -t meilisearch-session
#replace `barryallen@16` with your preferred masterkey .
./meilisearch --master-key="barryallen@16"
```
press `ctrl + b` , then `d` to detach from the tmux session. this helps to keep your meilisearch session running even after disconneting from server.
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
## Updating 
you would have to manually redo the all vidx extraction process again through `yt-dlp` so that you would have the updated all vidx over time.
then we find the unprocessed vidx from the now updated all vidx file to perform the extraction.
```bash
yt-dlp -v --cookies extraction-code/input/youtube-netscape-cookie.txt --flat-playlist --print id "https://www.youtube.com/feed/subscriptions" > extraction-code/input/subs_feed_video_ids.txt
``` 
if the log shows the cookie is no longer valid. do the steps 2 - 7 and re-run the above command.
then
```
# change the `PROCESS_UNPROCESSED` to `True` in extraction-code/scrapy-implementation.py
uv run extraction-code/scrapy-implementation.py
```
and update the meilisearch 
```
cd extraction-code\output
# replace \ with ^ if using cmd, \ is for bash shell
curl \
  -X POST "MEILISEARCH_URL/indexes/yt-ssf/documents?primaryKey=id" \
  -H "Content-Type: application/x-ndjson" \
  -H "Authorization: Bearer barryallen@16" \
  --data-binary @scrapy-extract.jsonl
  curl \
    -X GET "MEILISEARCH_URL/tasks/0" \
    -H "Authorization: Bearer barryallen@16"
```
To check the total number of documents (data count) in your Meilisearch index (yt-ssf)
```
 curl \
  -X GET "https://adhi.isroot.in/indexes/yt-ssf/stats" \
  -H "Authorization: Bearer barryallen@16"
```
## Playlists & courses
along with the videos, you can also extract all the playlists and courses links (with title) from every channel you are subscribed to. and also the total time and views of each playlist/course.
1. get all the channel ids from your subscriptions feed and save it. 
```bash
yt-dlp --cookies extraction-code/input/youtube-netscape-cookie.txt --flat-playlist --print "%(channel_id)s" "https://www.youtube.com/feed/channels" > extraction-code/input/sub-channels.txt
```
2. then run the channel playlists script, which goes through each channel and stores the playlists and courses links separately. 
```
uv run extraction-code/extract-channel-playlists.py
```
this writes to `extraction-code/output/channel-playlists.jsonl` and `extraction-code/output/channel-courses.jsonl`. if a channel has no playlists or courses tab, yt-dlp will log an error and move on. safe to ignore.
3. then run the enrich script to calculate the total time, video count and playlist views of each playlist/course. 
```
uv run extraction-code/enrich-playlist-stats.py
```
this adds `total_duration_seconds`, `total_duration_text` (HH:MM:SS), `video_count` and `playlist_views` (the playlist page's own views, not summed video views) to the same jsonl files. rerun it anytime for new playlists, it skips what is already done. use `--limit 3` to test on 3 playlists first. use `--mode backfill` to fill in the playlist `thumbnail_url` and `channel_name` needed for the website cards.
4. upload the playlists and courses to meilisearch. replace `MEILISEARCH_URL` with the actual url and run 
```
cd extraction-code\output
curl ^
  -X POST "MEILISEARCH_URL/indexes/yt-playlists/documents?primaryKey=id" ^
  -H "Content-Type: application/x-ndjson" ^
  -H "Authorization: Bearer barryallen@16" ^
  --data-binary @channel-playlists.jsonl
curl ^
  -X POST "MEILISEARCH_URL/indexes/yt-courses/documents?primaryKey=id" ^
  -H "Content-Type: application/x-ndjson" ^
  -H "Authorization: Bearer barryallen@16" ^
  --data-binary @channel-courses.jsonl
```
5. make duration and views sortable on the website. use `PATCH` here, `PUT` on `/settings` gives 405 through the caddy proxy.
```
curl ^
  -X PATCH "MEILISEARCH_URL/indexes/yt-playlists/settings" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer barryallen@16" ^
  --data "{\"sortableAttributes\": [\"total_duration_seconds\", \"playlist_views\", \"video_count\"]}"
curl ^
  -X PATCH "MEILISEARCH_URL/indexes/yt-courses/settings" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer barryallen@16" ^
  --data "{\"sortableAttributes\": [\"total_duration_seconds\", \"playlist_views\", \"video_count\"]}"
```
6. open the website and use the Videos / Playlists / Courses buttons above the results. playlist and course cards show the thumbnail with video count on the left and total time on the bottom right. a sort dropdown (longest, shortest, most viewed) appears on the playlists and courses tabs.

## Hosting
When you fork this repo and host the html in github pages. you cant make requests to http meilisearch endpoint url (Meilisearch doesn't natively handle SSL certificate generation and runs in http), as github pages uses https and you would get cors error.
### Solution 
- create a reverse proxy using caddy - [link](https://caddyserver.com/docs/install) in the vps you are self hosting meilisearch. 
- you would also need a registered domain or subdomain. you can obtain a free subdomain in [isroot.in](https://isroot.in/)
- open port 80 and 443 for http and https endpoints in your vps.
- after setting up your reverse proxy with caddy, you can check status by running
```bash
curl https://{YOUR_SUBDOMAIN}.isroot.in/health
```
- you should be seeing 
`{"status":"available"}` response.

## Future to-do
- [ ] create github actions to automatically fetch the new subscriber feed video ids and scrape those links with scrapy every 24 or 48 hours.