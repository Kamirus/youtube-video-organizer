#!/usr/bin/python

# python3

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

# Set DEVELOPER_KEY toW the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyCYa3J7eFc1tK5HUZDuUWV9_tY58dU3CSY"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(options):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    # q=options.q,
    type="video",
    # location=options.location,
    # locationRadius=options.location_radius,
    part="id,snippet",
    maxResults=options.max_results,
    order=options.order,
    publishedAfter=options.published_after,
    channelId=options.channel_id
  ).execute()

  search_videos = []

  # Merge video ids
  for search_result in search_response.get("items", []):
    search_videos.append(search_result["id"]["videoId"])
  video_ids = ",".join(search_videos)

  # Call the videos.list method to retrieve location details for each video.
  video_response = youtube.videos().list(
    id=video_ids,
    part='snippet, recordingDetails'
  ).execute()

  videos = []

  # Add each result to the list, and then display the list of matching videos.
  for video_result in video_response.get("items", []):
    videos.append("%s" % (video_result["snippet"]["title"]))

  print ("Videos:\n", "\n".join(videos), "\n")


if __name__ == "__main__":
  # argparser.add_argument("--q", help="Search term", default="Google")
  # argparser.add_argument("--location", help="Location", default="37.42307,-122.08427")
  # argparser.add_argument("--location-radius", help="Location radius", default="5km")
  # argparser.add_argument("--max-results", help="Max results", default=25)
  argparser.add_argument("--max-results", help="Max results", default=50)
  argparser.add_argument("--order", help="Order", default="date")
  argparser.add_argument("--published-after", help="beginning date", default="2016-05-07T00:00:00Z")
  argparser.add_argument("--channel-id", help="User", default="UCzuvRWjh7k1SZm1RvqvIx4w")

  args = argparser.parse_args()

  try:
    youtube_search(args)
  except HttpError as e:
    print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))