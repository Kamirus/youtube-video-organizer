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
  chlist = youtube.channels().list(
      forUsername=options.for_username,
      part="id"
  ).execute()

  print("User id for '{}': {}".format(options.for_username, chlist.get("items",[])[0]["id"]) )

if __name__ == "__main__":
  argparser.add_argument("--for-username", help="User", default="wybuchajacebeczki")

  args = argparser.parse_args()

  try:
    youtube_search(args)
  except HttpError as e:
    print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))