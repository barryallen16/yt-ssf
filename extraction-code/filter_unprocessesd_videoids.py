import json
from pathlib import Path
PARENT_DIR = Path(__file__).parent
INPUT_DIR = PARENT_DIR / "input"
ALL_SUBFEED_VIDX_FILEPATH = INPUT_DIR / "subs_feed_video_ids.txt"

OUTPUT_DIR = PARENT_DIR / "output"
EXTRACTED_JSONL_PATH = OUTPUT_DIR / "scrapy-extract.jsonl"
OUTPUT_FILEPATH = INPUT_DIR / "unprocessed_vidx.txt"
with open(ALL_SUBFEED_VIDX_FILEPATH, "r", encoding="utf-8") as f:
    all_vidx = {line.strip() for line in f if line.strip()}

with open(EXTRACTED_JSONL_PATH, "r", encoding="utf-8") as f:
    processed_vidx =set()
    for line in f:
        data = json.loads(line.strip())
        if data:
            processed_vidx.add(data["id"])
print(f"Found {len(all_vidx)} video ids in subfeed. Found {len(processed_vidx)} video ids already processed.")
unprocessed_vidx = all_vidx.difference(processed_vidx)
print(f"Found {len(unprocessed_vidx)} unprocessed video ids.")
with open(OUTPUT_FILEPATH, "w", encoding="utf-8") as f:
    for vidx in unprocessed_vidx:
        f.write(vidx + "\n")
print(f"Written {len(unprocessed_vidx)} unprocessed video ids to {OUTPUT_DIR}")