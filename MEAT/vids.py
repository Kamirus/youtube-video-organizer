#!/usr/bin/env python3

from apiclient.discovery import build
from apiclient.errors import HttpError
import argparse
import json
import os
from showYoutubers import View
from editYoutubers import getFullPathOfScript

'''

* tags: edit, show

'''


class Vids:
    # Variables
    #     self.__folderPath - path to folder where we will be storing files with video info
    #     self.__youtubersPath - path to json dict with youtubers
    #     self.__youtubers - loaded json youtubers

    def __init__(self, folderPath="raw/youtubers/", youtubersPath="raw/youtubers.txt"):
        self.__folderPath = getFullPathOfScript()+folderPath
        self.__youtubersPath = getFullPathOfScript()+youtubersPath
        self.__loadYoutubersFile()

    def updateAllYoutubers(self, Quick=False, All=False):
        for id, _ in self.__youtubers.items():
            self.updateYoutuber(id,Quick,All)

    def updateYoutuber(self, id, Quick=False, All=False):
        try:
            oneYoutuber = self.__youtubers[id]
        except:
            raise ValueError("[ERROR]\nNot found ID in youtubers file!")

        # First time!
        if oneYoutuber['channelName'] not in os.listdir(self.__folderPath):
            print("Init file for %s" % oneYoutuber['channelName'])

            # search vids
            JJ = self.__callSearch(oneYoutuber,id)

            # save to file
            self.__initFile(JJ,oneYoutuber['channelName'])

        # Just update
        else:
            try:
                # load old list of videos
                vids = self.__loadJson( oneYoutuber['channelName'] )

                # Want to make whole refresh
                if All:
                    date = oneYoutuber['publishedAfter']
                else:
                    date = self.__incrementFullDate(vids[0]['date'])

                # search
                JJ = self.__callSearch(oneYoutuber,id,date)

                # merging into vids
                if Quick:
                    for toAdd in JJ:
                        print('qNEW: {} by {:<}'.format(toAdd['title'],oneYoutuber['channelName']))
                        self.__quickMergeAssistant(toAdd,vids,0)
                else:
                    JJ.reverse()
                    for toAdd in JJ:
                        print('NEW: {} by {:<}'.format(toAdd['title'],oneYoutuber['channelName']))
                        self.__preciseMergeAssistant(toAdd,vids)

                self.__saveFile(vids,oneYoutuber['channelName'])

            except:
                raise ValueError("[ERROR]\nProblem occured while loading...")

    def removeVids(self, id):
        if self.__youtubers[id]['channelName'] in os.listdir(self.__folderPath):
            os.remove(self.__folderPath+self.__youtubers[id]['channelName'])
            print("Removed %s" % self.__youtubers[id]['channelName'])
        else:
            print("Nothing to be removed")

    def __callSearch(self,oneYoutuber,id, date=None):
        # Maybe we dont want to update all vids but only check for new ones
        if date == None:
            date = oneYoutuber['publishedAfter']

        yt = YTApi()
        if oneYoutuber['idType'] == 'username':
            return yt.youtube_search(id,date,True)
        else:
            return yt.youtube_search(id,date)

    # init file so it overwrites it
    def __initFile(self,outputJson, fileName):
        try:
            file = open(self.__folderPath+ fileName, 'w')
            json.dump(outputJson, file, indent=4,ensure_ascii=False)
            file.close()
        except:
            raise ValueError("[ERROR]\nProblem occured while saving...")

    # Safely overwrite file
    def __saveFile(self, outputJson, fileName):
        try:
            # Save changed database to temporary file
            file = open(self.__folderPath+ fileName + ".tmp", 'w')
            json.dump(outputJson, file, indent=4,ensure_ascii=False)
            file.close()

            # Now we are safely swaping these files and removing source
            os.rename(self.__folderPath+fileName, self.__folderPath+fileName + ".remove")
            os.rename(self.__folderPath+fileName + ".tmp", self.__folderPath+fileName)
            os.remove(self.__folderPath+fileName + ".remove")
        except:
            raise ValueError("[ERROR]\nProblem occured while saving...")

    def __loadJson(self, fileName):
        try:
            file = open(self.__folderPath+fileName, 'r')
            ret = json.load(file)
            file.close()
            return ret
        except:
            raise ValueError("[ERROR]\nProblem occured while loading...")

    def __loadYoutubersFile(self):
        # Fill youtubers with json file
        try:
            file = open(self.__youtubersPath, 'r')
            self.__youtubers = json.load(file)
            file.close()
        except:
            raise ValueError("[ERROR]\ncannot load file with youtubers")

    # merge two dictionaries
    def __mergeDicts(self, new, old):
        for key,val in new.items():
            if key != 'tags':
                old[key] = val
        return old

    # Quick adding! We are merging results based on date, if the same
    # video was republished then we will end up with same video twice
    # toAdd is just dict, vids is a list of dicts
    def __quickMergeAssistant(self,toAdd,vids,i):
        if toAdd['date'] > vids[i]['date']:
            vids.append(toAdd)
        elif toAdd['date'] == vids[i]['date']:
            vids[i] = self.__mergeDicts(toAdd, vids[i])
            i += 1
        else: # strange case:
            i = self.__quickMergeAssistant(toAdd,vids,i+1)
        return i

    # toAdd is just dict, vids is a list of dicts
    def __preciseMergeAssistant(self,toAdd,vids):
        for k in range(len(vids)):
            if toAdd['link'] == vids[k]['link']:
                self.__mergeDicts(toAdd,vids[k])
                return
        vids.insert(0,toAdd)

    # date = 2016-05-27T18:00:09.000Z
    def __incrementFullDate(self,date):
        backup = date
        # date[0] = 2016-05-27 | date[1] = 18:00:09.000Z
        date = date.split('T')

        # date[1] = [18,00,09]
        date[1] = date[1].split('.')[0].split(':')

        if date[1][2] == "59":
            if date[1][1] == "59":
                if date[1][0] == "23":
                    # problem...
                    return backup
                else:# +1
                    date[1][0] = "{:02}".format(int(date[1][0])+1)
            else:# +1
                date[1][1] = "{:02}".format(int(date[1][1])+1)
        else: # +1
            date[1][2] = "{:02}".format(int(date[1][2])+1)

        return '%sT%s.000Z' % (date[0], ':'.join(date[1]))

# Extend View from youtubers
class VidsView(View):
    class exList(list):
        # listv2 with items() like dictionary!
        def items(self):
            return ((i, self[i]) for i in range(len(self)) )
        def __str__(self):
            tmp = super().__str__()
            return ','.join(  tmp[2:-2].split("', '")  )


    def __init__(self, OrderList, Youtubers, Tags=None, folderPath="raw/youtubers/"):
        super().__init__(OrderList)
        self._youtubers = Youtubers # id's of youtubers
        self._tags = Tags
        self._folderPath = getFullPathOfScript()+folderPath

    # path is here for youtubers.txt not videos
    def show(self, nest=0, lines=False, printMain=False,
             headingChar='=',heading=True):

        # Take youtuber names from id's
        ytNames = self._getYTNames()

        # Number of columns
        col = os.get_terminal_size().columns

        # Width for one element in a row
        space = self.getSpace(ytNames,self._keylist,printMain=printMain)

        if heading:
            # Make a nice heading with key
            self._heading(space, printMain=printMain, char=headingChar)

        for name in ytNames:
            # load file
            self._loadFile(self._folderPath+name)

            # remove these vids without correct tags
            Nothing,self._source = self.__omitVidsWithoutTags(self._source,self._tags)

            if Nothing:
                continue

            tmp = self.exList()
            tmp.extend(self._source)
            self._source = tmp

            # ... and print author
            # print("")
            tool._printFramedWord(name,len(name))

            # Print main content
            self._printValues(nest, self._source, space, col,
                           lines=lines,
                           printMain=printMain,
                              notPipe='|')

    def _getYTNames(self, path="raw/youtubers.txt"):
        # Take youtuber names from id's
        self._loadFile(getFullPathOfScript()+path)

        try:
            return [ self._source[i]['channelName'] for i in self._youtubers ]
        except:
            return self._youtubers

    def getFolderPath(self):
        return self._folderPath

    def getSpace(self,ytNames, keyList, printMain):
        space = []

        # init empty lists
        for k in keyList:
            space.append([])

        if printMain:
            space.append([])

        # for every file ...
        for name in ytNames:
            self._loadFile(self._folderPath+name)

            i = 0
            if printMain:
                tmp = 1+len(str(len(self._source)))
                if tmp < 3: tmp=3

                space[i].append( tmp )
                i+=1
            #... => for every key
            for key in keyList:
                space[i].append(1+max(len(str(dic[key])) for dic in self._source ))
                i += 1

        # [[1,2,3],[3,3,5],[2,5,2]]
        return [ max(elist) for elist in space ]

    def _loadFile(self,filePath):
        super()._loadFile(filePath)

        try:
            # test = self._source[0]['tags']
            # change normal list with Tags into exList
            for dic in self._source:
                tmp = self.exList()
                tmp.extend(dic['tags'])
                dic['tags'] = tmp
        except:
            pass

    # returns a tuple (bool: Nothing, list: List)
    def __omitVidsWithoutTags(self,listDicts, Tags):
        Tags = set(Tags)
        tmp =  map( lambda dict:
             dict if Tags < set(dict['tags'])
                and 'SHOW' in set(dict['tags'])
                and 'SEEN' not in set(dict['tags'])
             else {},
             listDicts
        )
        # We want to check if there is anything interesting
        tmp = list(tmp)

        for x in tmp:
            if x != {}:
                return False, tmp

        # nothing!
        return True, tmp


class YTApi:
    # important Constants
    DEVELOPER_KEY = "AIzaSyCYa3J7eFc1tK5HUZDuUWV9_tY58dU3CSY"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    def GetChannelIdByUsername(self,Username):
        youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
        developerKey=self.DEVELOPER_KEY)

        return youtube.channels().list(
          forUsername=Username,
          part="id"
        ).execute().get("items",[])[0]["id"]

    # returns a dictionary of videos for given id
    def youtube_search(self,id, published_after, isUsername=False):
        youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
            developerKey=self.DEVELOPER_KEY)

        # Call the search.list method to retrieve results matching the specified
        # query term.

        if isUsername:
            id = self.GetChannelIdByUsername(id)

        vids = []

        vids = self.__onePageYoutubeSearch(vids,youtube,id,published_after)

        return vids

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
            vids.append({
                'title': video_result["snippet"]["title"],
                'duration': self.reformatISODate(video_result['contentDetails']['duration']),
                # 'duration': video_result['contentDetails']['duration'],
                'link': 'www.youtube.com/watch?v='+video_result["id"],
                'date': video_result['snippet']['publishedAt'],
                # 'description': video_result["snippet"]["description"],
                'tags': ['SHOW']
            })

        # return vids
        if Next == None or Next == 'None':
            return vids
        else: # next page
            return self.__onePageYoutubeSearch(vids,youtube,id,published_after,pageToken=Next)

    # iso = PT#H#M#S
    def reformatISODate(self, iso):
        try:
            h,m,s = 0,0,0
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

            return "{:02}:{:02}:{:02}".format(h,m,s)
        except:
            return "ERROR-DATE"


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--show",help="type youtuber id's or channelNames(name of the file with videos) which videos will be displayed.", nargs='*')
    parser.add_argument("--tags",help="Enter lowercase tags to filter display or add them to video",default={}, nargs='*')
    parser.add_argument("--remove",help="Remove file with videos by giving id")
    parser.add_argument("-u", "--update",default=False,nargs='?', help="With no argument: update all youtubers, with given id only update that one youtuber")
    # parser.add_argument("-p", "--precise", help="flag for update to merge precisely, can be little bit longer", action='store_true')
    parser.add_argument("-a", "--all", help="flag for update to check ALL videos once again", action='store_true')
    parser.add_argument("-c", "--clear", help="Clear terminal before printing anything", action='store_true')
    parser.add_argument("-t", "--table", help="Show results in a table", action='store_true')

    parser.add_argument("--test", action='store_true')

    args = parser.parse_args()

    if args.clear: os.system("clear")


    if args.test:
        print( getFullPathOfScript() )
        quit(0)


    if args.update != False:
        tool = Vids()
        print("Updating...")
        if args.update == None:
            tool.updateAllYoutubers(All=args.all)
        else:
            tool.updateYoutuber(args.update,All=args.all)
    elif args.remove != None:
        tool = Vids()
        tool.removeVids(args.remove)
    elif args.show != None:
        Cols = ['title','duration','link']

        if args.tags != {}:
            Cols.append('tags')

        # Show all of them
        if args.show == []:
            # init class
            tmp = VidsView(None,None,None)

            # get all youtubers
            args.show = os.listdir(  tmp.getFolderPath()  )

        # Call .show with chosen youtubers
        tool = VidsView(Cols,args.show,args.tags )
        tool.show(0,lines=args.table,printMain=True)