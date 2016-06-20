from apiclient.discovery import build
from apiclient.errors import HttpError
from Settings import Settings

# Handles yt api queries
class YTApi:
    def __init__(self):
        # important Constants
        self.settings = Settings()
        # Unique api key from settings
        self.OWN_DEV_KEY = self.settings['apiKey']
        self.YOUTUBE_API_SERVICE_NAME = "youtube"
        self.YOUTUBE_API_VERSION = "v3"
        # build
        self.youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
                            developerKey=self.OWN_DEV_KEY)

    def GetChannelIdByUsername(self, Username):
        return self.youtube.channels().list(
            forUsername=Username,
            part="id"
        ).execute().get("items", [])[0]["id"]

    # returns a list of videos for given id
    def youtube_search(self, id, published_after, isUsername=False):
        # Call the search.list method to retrieve results matching the specified
        # query term.

        if isUsername:
            id = self.GetChannelIdByUsername(id)

        vids = []

        vids = self.__onePageYoutubeSearch(vids, self.youtube, id, published_after)

        return vids

    # can raise ValueError or other http err
    # Tuple = (uOrC, userOrChannelID)
    @staticmethod
    def getChannelName(Tuple):

        # Unique api key from settings
        OWN_DEV_KEY = Settings()['apiKey']
        YOUTUBE_API_SERVICE_NAME = "youtube"
        YOUTUBE_API_VERSION = "v3"
        # build
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                            developerKey=OWN_DEV_KEY)

        (uOrID, userOrChannelID) = Tuple
        if uOrID.casefold() == 'u':
            for_username = userOrChannelID

            chlist = youtube.channels().list(
                forUsername=for_username,
                part="snippet"
            ).execute()

            return chlist.get("items", [])[0]["snippet"]["title"]
        elif uOrID.casefold() == 'c':
            ID = userOrChannelID

            chlist = youtube.channels().list(
                id=ID,
                part="snippet"
            ).execute()

            return chlist.get("items", [])[0]["snippet"]["title"]
        else:
            raise ValueError('Wrong TUPLE, First argument can be: U or C')

    # it adds to vids desired search results recursively page by page
    def __onePageYoutubeSearch(self, vids, youtube, id, published_after, pageToken=None):
        # ask youtube
        search_response = youtube.search().list(
            type="video",
            part="id,snippet",
            maxResults=50,
            order="date",
            publishedAfter=published_after,
            channelId=id,
            pageToken=pageToken
        ).execute()

        search_videos = []

        # Next page cuz 50 results is not enough
        Next = search_response.get("nextPageToken")

        # Merge video ids
        for search_result in search_response.get("items", []):
            search_videos.append(search_result["id"]["videoId"])
        video_ids = ",".join(search_videos)

        # Call the videos.list method to retrieve details for each video.
        video_response = youtube.videos().list(
            id=video_ids,
            part='snippet, contentDetails'
        ).execute()

        # Add each result to the list
        for video_result in video_response.get("items", []):
            # title
            title = video_result["snippet"]["title"]
            if self.settings['maxCharsForTitle'] != None:
                title = title[:self.settings['maxCharsForTitle']]

            vids.append({
                'title': title,
                'duration': self.reformatISODate(video_result['contentDetails']['duration']),
                # 'duration': video_result['contentDetails']['duration'],
                'link': 'www.youtube.com/watch?v=' + video_result["id"],
                'date': video_result['snippet']['publishedAt'],
                # 'description': video_result["snippet"]["description"],
                'tags': [],
                'show': True,
                'seen': False
            })

        # return vids
        if Next == None or Next == 'None':
            return vids
        else:  # next page
            return self.__onePageYoutubeSearch(vids, youtube, id, published_after, pageToken=Next)

    # iso = PT#H#M#S
    def reformatISODate(self, iso):
        try:
            h, m, s = 0, 0, 0
            # make it clean #H#M#S
            iso = iso.split('T')[1]

            # cut hours iso=#M#S
            if 'H' in iso:
                tmp = iso.split('H')
                h = int(tmp[0])
                iso = tmp[1]

            # cut minutes iso=#S
            if 'M' in iso:
                tmp = iso.split('M')
                m = int(tmp[0])
                iso = tmp[1]

            if 'S' in iso:
                tmp = iso.split('S')
                s = int(tmp[0])

            return "{:02}:{:02}:{:02}".format(h, m, s)
        except:
            return "ERROR-DATE"
