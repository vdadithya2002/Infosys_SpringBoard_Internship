import requests
import pandas as pd
import os

API_KEY = os.environ.get("YOUTUBE_API_KEY")  # Set via environment variable
CHANNEL_ID = os.environ.get("CHANNEL_ID")  # Set via environment variable

# 1. Get 50 video IDs
search_url = "https://www.googleapis.com/youtube/v3/search"
params = {
    "key": API_KEY,
    "channelId": CHANNEL_ID,
    "part": "id",
    "order": "date",
    "maxResults": 50,
    "type": "video"
}
res = requests.get(search_url, params=params).json()
video_ids = [item["id"]["videoId"] for item in res["items"]]

# 2. Get video details
videos_url = "https://www.googleapis.com/youtube/v3/videos"
params = {
    "key": API_KEY,
    "id": ",".join(video_ids),
    "part": "snippet,contentDetails,statistics,status"
}
res_v = requests.get(videos_url, params=params).json()

rows = []
for item in res_v["items"]:
    snip = item["snippet"]
    stats = item.get("statistics", {})
    cd = item.get("contentDetails", {})
    status = item.get("status", {})

    rows.append({
        "id": item["id"],
        "title": snip.get("title"),
        "description": snip.get("description"),
        "publishedAt": snip.get("publishedAt"),
        "tags": ",".join(snip.get("tags", [])),
        "categoryId": snip.get("categoryId"),
        "defaultLanguage": snip.get("defaultLanguage"),
        "defaultAudioLanguage": snip.get("defaultAudioLanguage"),
        "thumbnail_default": snip.get("thumbnails", {}).get("default", {}).get("url"),
        "thumbnail_high": snip.get("thumbnails", {}).get("high", {}).get("url"),
        "duration": cd.get("duration"),
        "viewCount": stats.get("viewCount"),
        "likeCount": stats.get("likeCount"),
        "commentCount": stats.get("commentCount"),
        "privacyStatus": status.get("privacyStatus")
    })

df_videos = pd.DataFrame(rows)

# 3. Get channel info
channel_url = "https://www.googleapis.com/youtube/v3/channels"
params = {
    "key": API_KEY,
    "id": CHANNEL_ID,
    "part": "snippet,statistics"
}
res_c = requests.get(channel_url, params=params).json()
chan = res_c["items"][0]
csnip = chan["snippet"]
cstats = chan["statistics"]

channel_info = {
    "channel_id": chan["id"],
    "channel_title": csnip.get("title"),
    "channel_description": csnip.get("description"),
    "channel_country": csnip.get("country"),
    "channel_thumbnail": csnip.get("thumbnails", {}).get("default", {}).get("url"),
    "channel_subscriberCount": cstats.get("subscriberCount"),
    "channel_videoCount": cstats.get("videoCount"),
}

# Add channel fields to every row
for k, v in channel_info.items():
    df_videos[k] = v

# 4. Save to CSV
df_videos.to_csv("nikhil_kamath_50_videos.csv", index=False)
