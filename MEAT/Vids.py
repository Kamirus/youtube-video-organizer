import json, os
from Settings import getFullPathOfScript
from YTApi import YTApi
from Settings import Settings


# Main 'abstract' class
class Vids:
    # Variables
    #     self._folderPath - path to folder where we will be storing files with video info
    #     self._youtubersPath - path to json dict with youtubers
    #     self._youtubers - loaded json youtubers

    def __init__(self, folderPath="raw/youtubers/", youtubersPath="raw/youtubers.txt"):
        self._folderPath = getFullPathOfScript() + folderPath
        self._youtubersPath = getFullPathOfScript() + youtubersPath
        self._loadYoutubersFile()

    # Returns read json
    def _loadJson(self, fileName):
        try:
            file = open(self._folderPath + fileName, 'r')
            ret = json.load(file)
            file.close()
            return ret
        except:
            raise ValueError("[ERROR]\nProblem occured while loading...")

    # Safely overwrite file
    def _saveFile(self, outputJson, fileName):
        try:
            # Save changed database to temporary file
            file = open(self._folderPath + fileName + ".tmp", 'w')
            json.dump(outputJson, file, indent=4, ensure_ascii=False)
            file.close()

            # Now we are safely swaping these files and removing source
            os.rename(self._folderPath + fileName, self._folderPath + fileName + ".remove")
            os.rename(self._folderPath + fileName + ".tmp", self._folderPath + fileName)
            os.remove(self._folderPath + fileName + ".remove")
        except:
            raise ValueError("[ERROR]\nProblem occured while saving...")

    # Fills _youtubers
    def _loadYoutubersFile(self):
        # Fill youtubers with json file
        try:
            file = open(self._youtubersPath, 'r')
            self._youtubers = json.load(file)
            file.close()
        except:
            raise ValueError("[ERROR]\ncannot load file with youtubers")


# Inits and Updates videos
class UpdateVids(Vids):
    def __init__(self):
        super().__init__()
        self._ss = Settings()

    def updateAllYoutubers(self, All=False):
        for id, _ in self._youtubers.items():
            self.updateYoutuber(id, All)

    def updateYoutuber(self, id, All=False):
        try:
            oneYoutuber = self._youtubers[id]
        except:
            raise ValueError("[ERROR]\nNot found ID in youtubers file!")

        # First time!
        if oneYoutuber['channelName'] not in os.listdir(self._folderPath):
            print("Init file for %s" % oneYoutuber['channelName'])

            # search vids
            JJ = self._callSearch(oneYoutuber, id)

            # save to file
            self._initFile(JJ, oneYoutuber['channelName'])

        # Just update
        else:
            try:
                # load old list of videos
                vids = self._loadJson(oneYoutuber['channelName'])

                # Want to make whole refresh
                if All:
                    date = oneYoutuber['publishedAfter']
                else:
                    date = self._incrementFullDate(vids[0]['date'])

                # search
                JJ = self._callSearch(oneYoutuber, id, date)

                # merging into vids

                JJ.reverse()
                for toAdd in JJ:
                    print('NEW: {} by {:<}'.format(toAdd['title'], oneYoutuber['channelName']))
                    self._preciseMergeAssistant(toAdd, vids)

                self._saveFile(vids, oneYoutuber['channelName'])

            except:
                raise ValueError("[ERROR]\nProblem occured while loading...")

    # returns YTApi().youtube_search(id,date)
    def _callSearch(self, oneYoutuber, id, date=None):
        # Maybe we dont want to update all vids but only check for new ones
        if date == None:
            date = oneYoutuber['publishedAfter']

        yt = YTApi()
        if oneYoutuber['idType'] == 'username':
            return yt.youtube_search(id, date, True)
        else:
            return yt.youtube_search(id, date)

    # init file with vids, so it overwrites it
    def _initFile(self, outputJson, fileName):
        try:
            file = open(self._folderPath + fileName, 'w')
            json.dump(outputJson, file, indent=4, ensure_ascii=False)
            file.close()
        except:
            raise ValueError("[ERROR]\nProblem occured while saving...")

    # merge two dictionaries
    def _mergeDicts(self, new, old):
        for key, val in new.items():
            if key not in self._ss['dontChangeValuesInThatListWhileUpdatingAll']:
                old[key] = val
        return old

    # toAdd is just dict, vids is a list of dicts
    def _preciseMergeAssistant(self, toAdd, vids):
        for k in range(len(vids)):
            if toAdd['link'] == vids[k]['link']:
                self._mergeDicts(toAdd, vids[k])
                return
        vids.insert(0, toAdd)

    # date = 2016-05-27T18:00:09.000Z
    def _incrementFullDate(self, date):
        backup = date
        # date[0] = 2016-05-27 | date[1] = 18:00:09.000Z
        date = date.split('T')

        # date[1] = [18,00,09]
        date[1] = date[1].split('.')[0].split(':')

        if date[1][2] == "59":
            date[1][2] = "00"
            if date[1][1] == "59":
                date[1][1] = "00"
                if date[1][0] == "23":
                    # problem...
                    return backup
                else:  # +1
                    date[1][0] = "{:02}".format(int(date[1][0]) + 1)
            else:  # +1
                date[1][1] = "{:02}".format(int(date[1][1]) + 1)
        else:  # +1
            date[1][2] = "{:02}".format(int(date[1][2]) + 1)

        return '%sT%s.000Z' % (date[0], ':'.join(date[1]))


# Just for removing files with videos
class RemoveVids(Vids):
    def __init__(self):
        super().__init__()

    def removeVids(self, id):
        if self._youtubers[id]['channelName'] in os.listdir(self._folderPath):
            os.remove(self._folderPath + self._youtubers[id]['channelName'])
            print("Removed %s" % self._youtubers[id]['channelName'])
        else:
            print("Nothing to be removed")


class EditVids(Vids):
    # model for public methods below
    def __edit(self, youtuber: str, ids: list, seen=None, show=None, tags=None, remove=False):
        fileName = self._getYTName(youtuber)
        ytvids = self._loadJson(fileName)  # :list

        if seen != None:
            for id in ids:
                ytvids[id]['seen'] = seen
        elif show != None:
            for id in ids:
                ytvids[id]['show'] = show
        elif tags != None:
            if remove:
                for id in ids:
                    ytvids[id]['tags'] = self._removeTagsFromList(ytvids[id]['tags'],tags)
            else:
                for id in ids:
                    ytvids[id]['tags'] = self._addTagsToList(ytvids[id]['tags'],tags)

        self._saveFile(ytvids,fileName)

    def seen(self, youtuber: str, ids: list, seen=True):
        self.__edit(youtuber,ids,seen=seen)

    def show(self, youtuber: str, ids: list, show=True):
        self.__edit(youtuber,ids,show=show)

    def addTags(self, youtuber: str, ids: list, tags: list):
        self.__edit(youtuber,ids,tags=tags)

    def removeTags(self, youtuber: str, ids: list, tags: list):
        self.__edit(youtuber,ids,tags=tags,remove=True)

    # Take youtuber names from id's
    def _getYTName(self, youtuber: str) -> str:
        try:
            return self._youtubers[youtuber]['channelName']
        except:
            return youtuber

    def _addTagsToList(self, preList:list, tags:list):
        for tag in tags:
            if tag not in preList:
                preList.append(tag)
        return preList

    def _removeTagsFromList(self, preList:list, tags:list):
        for tag in tags:
            if tag in preList:
                preList.remove(tag)
        return preList

