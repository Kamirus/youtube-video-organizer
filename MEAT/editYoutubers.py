#!/usr/bin/env python3

import argparse, json, os, datetime
from Settings import getFullPathOfScript,Settings
from YTApi import YTApi


class EditYoutubers:
    __date = '1970-01-01'

    def __init__(self):
        self.__settings = Settings()
        # i need that in order to delete files with videos after removing youtuber
        self.__pathToYoutubersDir = getFullPathOfScript()+self.__settings['paths']['youtubersFolder']

        # path to youtubers.txt
        self.__path = '{}{}{}'.format(getFullPathOfScript(),
                                      self.__settings['paths']['rawFolder'],
                                      'youtubers.txt')
        self.__source = None
        dir_file = self.__path.rsplit('/', maxsplit=1)
        if dir_file[1] not in os.listdir(dir_file[0]):
            try:
                file = open(self.__path, 'w')
                file.write("{}")
                file.close()
            except Exception as e:
                raise ValueError("Cannot initialize youtubers.txt file\n%s" % e)

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
            raise ValueError("[ERROR] \n%s" % e)

    def AddYouTuberByUsername(self, id, publishedAfter=__date):
        self.AddYouTuber(id, "username", publishedAfter)

    def AddYouTuberByChannelId(self, id, publishedAfter=__date):
        self.AddYouTuber(id, "channelId", publishedAfter)

    def RemoveYoutuber(self, id):
        # Load database
        if self.__source == None:
            self.__loadFile()

        try:
            try: # need to delete his file with videos
                os.remove(self.__pathToYoutubersDir+self.__source[id]['channelName'])
            except:
                pass

            del (self.__source[id])
        except Exception as e:
            raise ValueError("[ERROR] Nothing to be removed \n%s" % e)

        self.__saveFile()

    def __show(self):
        try:
            file = open(self.__path, 'r')
            print(json.dumps(json.load(file), indent=4, ensure_ascii=False))
            file.close()
        except Exception as e:
            raise ValueError("[ERROR] Cannot 'Show', something went wrong\n %s" % e)

    def __loadFile(self):
        try:
            file = open(self.__path, 'r')
            self.__source = json.load(file)
            file.close()
        except Exception as e:
            raise ValueError("[ERROR]\ncannot load file with youtubers\n%s" % e)

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
        except Exception as e:
            raise ValueError("[ERROR]\nProblem occured while saving...\n%s" % e)

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
