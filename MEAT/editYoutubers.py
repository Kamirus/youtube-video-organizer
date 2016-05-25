from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import argparse
import json
import os
import datetime


class editYoutubers:
    __date = '1970-01-01'

    def __init__(self,
                 path="raw/youtubers.txt"):
        self.__path = path
        self.__source = None
        dir_file = self.__path.rsplit('/', maxsplit=1)
        if dir_file[1] not in os.listdir(dir_file[0]):
            try:
                file = open(self.__path, 'w')
                file.write("{}")
                file.close()
            except:
                raise ValueError("Cannot initialize youtubers.txt file")

    def __show(self):
        try:
            file = open(self.__path, 'r')
            print(json.dumps(json.load(file), indent=4))
            file.close()
        except:
            raise ValueError("[ERROR]\nCannot 'Show', something went wrong")

    def __loadFile(self):
        try:
            file = open(self.__path, 'r')
            self.__source = json.load(file)
            file.close()
        except:
            raise ValueError("[ERROR]\ncannot load file with youtubers")

    def __saveFile(self):
        try:
            # Save changed database to temporary file
            file = open(self.__path + ".tmp", 'w')
            json.dump(self.__source, file, indent=4)
            file.close()

            # Now we are safely swaping these files and removing source
            os.rename(self.__path, self.__path + ".remove")
            os.rename(self.__path + ".tmp", self.__path)
            os.remove(self.__path + ".remove")
        except:
            raise ValueError("[ERROR]\nProblem occured while saving...")

    # idType = "username" | "channelId"
    # publishedAfter = 'YYYY-MM-DD'
    def AddYouTuber(self, id, idType, publishedAfter=__date):
        try:
            # Load database
            if self.__source == None:
                self.__loadFile()

            try:  # check if already there
                tmp = self.__source[id]
                print("Readding...")
                raise NameError("Catch me!")
            except:  # Adding...
                # Add item
                self.__source[id] = self.__fillMember(id,
                                                      idType,
                                                      publishedAfter)
                # Save changes safely
                self.__saveFile()
        # File is probably empty, fill it with {} and call method again
        except ValueError as e:
            raise ValueError("[ERROR]\n  ValueError\n  Check if the "
                             "youtubers.txt file is valid.\n Delete that file "
                             "and run script again or rename it, run script and "
                             "then merge changes manually", '\n', e)
        # other problem
        except Exception as e:
            print("[ERROR]\n", e)

    def AddYouTuberByUsername(self, id, publishedAfter=__date):
        self.AddYouTuber(id, "username", publishedAfter)

    def AddYouTuberByChannelId(self, id, publishedAfter=__date):
        self.AddYouTuber(id, "channelId", publishedAfter)

    # publishedAfter = "YEAR-MM-DD"
    def __fillMember(self, id, idType, publishedAfter):
        return {
            'idType': idType,
            'channelName': self.__getChannelName((idType[0], id)),
            'publishedAfter': self.__getProperDate(publishedAfter)
        }

    # Date = "1970-01-01"
    def __getProperDate(self, Date):
        try:
            datetime.datetime.strptime(Date, '%Y-%m-%d')
        except:
            Date = self.__date
            print('[ERROR]Wrong date, date set to default, readd to change that')
        finally:
            return Date + "T00:00:00Z"

    # can raise ValueError or other http err
    # Tuple = (uOrC, userOrChannelID)
    def __getChannelName(self, Tuple):
        DEVELOPER_KEY = "AIzaSyCYa3J7eFc1tK5HUZDuUWV9_tY58dU3CSY"
        YOUTUBE_API_SERVICE_NAME = "youtube"
        YOUTUBE_API_VERSION = "v3"

        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                        developerKey=DEVELOPER_KEY)

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--add", help="Add youtuber by giving username (-u) or " \
                                      "channelId (-c), related with -u -c --date" \
                                      " | example: python3 editYoutubers.py --add SomeUserName -u")
    parser.add_argument("--date", help="Videos published before this date:" \
                                       "YYYY-MM-DD will be omitted", type=str, default='1970-01-01')
    parser.add_argument("-u", help="add by username", action='store_true')
    parser.add_argument("-c", help="add by channel id", action='store_true')
    args = parser.parse_args()

    # If we can add
    if args.add != None and (args.u == True and args.c == False) or (args.c == True and args.u == False):
        if args.u == True:
            by = "username"
        else:
            by = "channelId"
        print("Adding {} by {}, published after:{}".format(args.add, by, args.date))
        Obj = editYoutubers()
        try:
            Obj.AddYouTuber(args.add, by, args.date)
        except Exception as e:
            print(e)
    else:
        print("Maybe use some --help? Nothing happened")
