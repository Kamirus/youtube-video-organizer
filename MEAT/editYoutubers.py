from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import json
import os

class editYoutubers:
    Authors = []
    Comments = []

    def __init__(self, path="raw/youtubers.txt"):
        self.__path = path

    def Show(self):
        file = open(self.__path,'r')
        print(json.dumps( json.load(file),indent=4 ))
        file.close()

    # idType = "username" | "channelId"
    def AddYouTuber(self, id, idType, publishedAfter="1970-01-01"):
        try:
            # Load database
            file = open(self.__path,'r')
            source = json.load(file)
            file.close()

            try: # check if already there
                tmp = source[id]
                raise NameError("Already something under that id!")
            except: # Adding...
                # Add item
                source[id] = self.__fillMember(id,idType,publishedAfter)

                # Save changed database to temporary file
                file = open(self.__path+".tmp",'w')
                json.dump(source,file, indent=4)
                file.close()

                # Now we are safely swaping these files and removing source
                os.rename(self.__path,self.__path+".remove")
                os.rename(self.__path+".tmp", self.__path)
                os.remove(self.__path+".remove")
        # File is probably empty, fill it with {} and call method again
        except ValueError as e:
            print("ValueError",'\n',e)
            file = open(self.__path,'w')
            file.write("{}")
            file.close()
            self.AddYouTuber(idType,publishedAfter)
        # other problem
        except Exception as e:
            print("Dunno what err\n",e)

    def AddYouTuberByUsername(self, id, publishedAfter="1970-01-01"):
        self.AddYouTuber(id, "username",publishedAfter)
    def AddYouTuberByChannelId(self, id, publishedAfter="1970-01-01"):
        self.AddYouTuber(id, "channelId",publishedAfter)

    # publishedAfter = "YEAR-MM-DD"
    def __fillMember(self, id, idType, publishedAfter):
        return  {
                    'idType': idType,
                    'channelName': self.__getChannelName( (idType[0],id) ),
                    'publishedAfter': self.__getProperDate(publishedAfter)
                }

    # Date = "1970-01-01"
    def __getProperDate(self, Date):
        return Date + "T00:00:00Z"

    # can raise NameError or other http err
    # Tuple = (uOrC, userOrChannelID)
    def __getChannelName(self, Tuple):
        DEVELOPER_KEY = "AIzaSyCYa3J7eFc1tK5HUZDuUWV9_tY58dU3CSY"
        YOUTUBE_API_SERVICE_NAME = "youtube"
        YOUTUBE_API_VERSION = "v3"

        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
            developerKey=DEVELOPER_KEY)


        (uOrID,userOrChannelID) = Tuple
        if uOrID.casefold() == 'u':
            for_username = userOrChannelID

            chlist = youtube.channels().list(
                forUsername=for_username,
                part="snippet"
            ).execute()

            return chlist.get("items",[])[0]["snippet"]["title"]
        elif uOrID.casefold() == 'c':
            ID = userOrChannelID

            chlist = youtube.channels().list(
                id=ID,
                part="snippet"
            ).execute()

            return chlist.get("items",[])[0]["snippet"]["title"]
        else:
            raise NameError('Wrong TUPLE, First argument can be: U or C')

ey = editYoutubers()
# ey.Edit()
ey.AddYouTuberByUsername("dmbrandon","2000-10-01")