#!/usr/bin/env python3

import argparse, json, os, datetime
from Settings import getFullPathOfScript
from YTApi import YTApi

# i need that in order to delete files with videos after removing youtuber
pathToYoutubersDir = getFullPathOfScript()+'raw/youtubers/'

class EditYoutubers:
    __date = '1970-01-01'

    def __init__(self, path="raw/youtubers.txt"):
        self.__path = getFullPathOfScript() + path
        self.__source = None
        dir_file = self.__path.rsplit('/', maxsplit=1)
        if dir_file[1] not in os.listdir(dir_file[0]):
            try:
                file = open(self.__path, 'w')
                file.write("{}")
                file.close()
            except:
                raise ValueError("Cannot initialize youtubers.txt file")

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

    def RemoveYoutuber(self, id):
        # Load database
        if self.__source == None:
            self.__loadFile()

        try:
            # need to delete his file with videos
            os.remove(pathToYoutubersDir+self.__source[id]['channelName'])

            del (self.__source[id])
        except:
            raise ValueError("Nothing to be removed")

        self.__saveFile()

    def __show(self):
        try:
            file = open(self.__path, 'r')
            print(json.dumps(json.load(file), indent=4, ensure_ascii=False))
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
            json.dump(self.__source, file, indent=4, ensure_ascii=False)
            file.close()

            # Now we are safely swaping these files and removing source
            os.rename(self.__path, self.__path + ".remove")
            os.rename(self.__path + ".tmp", self.__path)
            os.remove(self.__path + ".remove")
        except:
            raise ValueError("[ERROR]\nProblem occured while saving...")

    # publishedAfter = "YEAR-MM-DD"
    def __fillMember(self, id, idType, publishedAfter):
        return {
            'idType': idType,
            'channelName': YTApi.getChannelName((idType[0], id)),
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--remove", help="Remove youtuber by giving his id")
    parser.add_argument("-a", "--add", help="Add youtuber by giving username (-u) or " \
                                            "channelId (-c), related with -u -c --date" \
                                            " | example: python3 editYoutubers.py --add SomeUserName -u")
    parser.add_argument("-d", "--date", help="Videos published before this date:" \
                                             "YYYY-MM-DD will be omitted", type=str, default='1970-01-01')
    parser.add_argument("-U", help="add by username", action='store_true')
    parser.add_argument("-C", help="add by channel id", action='store_true')
    parser.add_argument("-c", "--clear", help="clear terminal before taking other actions", action='store_true')

    args = parser.parse_args()

    if args.clear:
        os.system("clear")

    # If we can add
    if args.add != None and (args.U == True and args.C == False) or (args.C == True and args.U == False):
        if args.U == True:
            by = "username"
        else:
            by = "channelId"
        print("Adding {} by {}, published after:{}".format(args.add, by, args.date))
        Obj = EditYoutubers()
        try:
            Obj.AddYouTuber(args.add, by, args.date)
        except Exception as e:
            print("[ERROR] = %s" % e)
    elif args.remove != None:
        Obj = EditYoutubers()
        print("Removing %s" % args.remove)
        try:
            Obj.RemoveYoutuber(args.remove)
        except Exception as e:
            print("[ERROR] = %s" % e)
    else:
        print("Maybe use some --help? Nothing happened")
