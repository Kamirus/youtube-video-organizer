#!/usr/bin/python

# python3

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

# important Constants
DEVELOPER_KEY = "AIzaSyCYa3J7eFc1tK5HUZDuUWV9_tY58dU3CSY"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def GetChannelIdByUsername(Username):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

    return youtube.channels().list(
      forUsername=Username,
      part="id"
    ).execute().get("items",[])[0]["id"]

def youtube_search(options):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    type="video",
    part="id,snippet",
    maxResults=options.max_results,
    order=options.order,
    publishedAfter=options.published_after,
    channelId=GetChannelIdByUsername(options.username)
  ).execute()

  search_videos = []

  # Merge video ids
  for search_result in search_response.get("items", []):
    search_videos.append(search_result["id"]["videoId"])
  video_ids = ",".join(search_videos)

  # Call the videos.list method to retrieve details for each video.
  video_response = youtube.videos().list(
    id=video_ids,
    part='snippet, recordingDetails'
  ).execute()

  videos = []

  # Add each result to the list, and then display the list of matching videos.
  for video_result in video_response.get("items", []):
      videos.append( (video_result["snippet"]["title"], video_result["id"]) )

  print("Videos:\n")
  for (a,b) in videos:
      print(a," ","www.youtube.com/watch?v="+b)


if __name__ == "__main__":
  argparser.add_argument("--max-results", help="Max results", default=50)
  argparser.add_argument("--order", help="Order", default="date")
  argparser.add_argument("--username", help="Username", default="wybuchajacebeczki")
  argparser.add_argument("--published-after", help="beginning date", default="2016-05-07T00:00:00Z")

  args = argparser.parse_args()

  try:
    youtube_search(args)
  except HttpError as e:
    print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))