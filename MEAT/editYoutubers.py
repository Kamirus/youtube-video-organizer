from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import os

class editYoutubers:
    Authors = []
    Comments = []

    def __init__(self, path="raw/youtubers.txt"):
        self.__path = path

    def Show(self):
        if self.Authors == []:
            self.__readFile()
        os.system("clear")
        i=0
        print("YouTube-Video-Organizer\nChosen ones:\nNr \tChannel Name",end="")
        for (_,ChannelName,_) in self.Authors:
            print( "\n{}\t{}".format(i,ChannelName), end="")
            i += 1

    def Edit(self):
        self.Show()
        world = input( "\nEnter (+) in order to add new author\n"
               "Enter number to edit existing author\n"
               "Enter anything else to exit\n")

        if '+' in world:
            os.system("clear")
            idorchannel = input("Type:\n"
                                "U if You want to enter author by his username\n"
                                "C if You want to enter author by his channel ID\n")
            if idorchannel.casefold().startswith('u'):
                idorchannel = input("Enter username: ")
                name = self.__getChannelName(('U',idorchannel))
                self.Authors.append(('U',name,idorchannel))
            elif idorchannel.casefold().startswith('c'):
                idorchannel = input("Enter channel ID: ")
                name = self.__getChannelName(('C',idorchannel))
                self.Authors.append(('C',name,idorchannel))
        elif world.isdecimal():
            print("zaraz bedzie")


    # can raise NameError or other http err
    # Tuple = (uOrC, userOrChannelID)
    def __getChannelName(self, Tuple):
        DEVELOPER_KEY = "AIzaSyCYa3J7eFc1tK5HUZDuUWV9_tY58dU3CSY"
        YOUTUBE_API_SERVICE_NAME = "youtube"
        YOUTUBE_API_VERSION = "v3"

        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
            developerKey=DEVELOPER_KEY)


        (uOrID,userOrChannelID) = Tuple
        if uOrID == 'U':
            for_username = userOrChannelID

            chlist = youtube.channels().list(
                forUsername=for_username,
                part="snippet"
            ).execute()

            return chlist.get("items",[])[0]["snippet"]["title"]
        elif uOrID == 'C':
            ID = userOrChannelID

            chlist = youtube.channels().list(
                id=ID,
                part="snippet"
            ).execute()

            return chlist.get("items",[])[0]["snippet"]["title"]
        else:
            raise NameError('Wrong TUPLE, First argument can be: U or C')

    def __readFile(self, AllNames=False):
        try:
            file = open( self.__path ,'r')
        except Exception as e:
            print(e)
            raise NameError(" NO SUCH FILE ")
        line = file.readline()

        while line != "":
            if line[0] == 'U' or line[0] == 'C':
                tmplist = line.split(' ; ')
                if tmplist[1] == '' or AllNames:
                    tmplist[1] = self.__getChannelName( (tmplist[0],tmplist[2]) )
                self.Authors.append( (tmplist[0], tmplist[1], tmplist[2][: -1]) )
            else:
                self.Comments.append(line)
            line = file.readline()
        file.close()

    def __writeToFile(self):
        file = open(self.__path, 'w')

        for x in self.Comments:
            file.write(x)

        for (Type, ChannelName, ID) in self.Authors:
            file.write( "{} ; {} ; {}\n".format(Type,ChannelName,ID) )

        file.close()

    def test(self):
        try:
            self.__readFile()
            self.__writeToFile()
            for elem in self.Authors:
                print(elem[0], ' ',elem[1], ' ',elem[2] )
        except NameError as e:
            print(e.args)

ey = editYoutubers()
ey.Edit()