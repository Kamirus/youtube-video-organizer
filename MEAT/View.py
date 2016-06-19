import os,json
from Settings import getFullPathOfScript,Settings

class View:
    # OrderList is a list with Keys that will be displayed
    def __init__(self, OrderList):
        self._settings = Settings()
        # path to youtubers.txt
        self._path = '{}{}{}'.format(getFullPathOfScript(),
                                      self._settings['paths']['rawFolder'],
                                      'youtubers.txt')
        self._source = None
        self._keylist = OrderList

    def show(self, nest=0, lines=False, printMain=False,
             headingChar='='):
        # load file
        self._loadFile(self._path)

        # Number of columns
        col = os.get_terminal_size().columns

        # Width for one element in a row
        space = []
        if printMain:
            space.append(1+max(len(i) for i,_ in self._source.items() ))
        for key in self._keylist:
            space.append(1+max(len(val[key]) for _,val in self._source.items() ))

        # Make a nice heading with key
        self._heading(space, printMain=printMain, char=headingChar)

        # Print main content
        self._printValues(nest, self._source, space, col,
                           lines=lines,
                           printMain=printMain)

    def _loadFile(self,filePath):
        try:
            file = open(filePath, 'r')
            self._source = json.load(file)
            file.close()
        except Exception as e:
            raise ValueError("[ERROR]\ncannot load file\n%s" % e)

    def _heading(self, space, printMain, char='='):
        # Line
        self._printLine(space)

        # id
        i=0
        if printMain:
            print('{0:{1}}'.format('|' + 'id', space[i]), end="")
            i+=1

        # key
        for elem in self._keylist:
            print('{0:{1}}'.format('|' + elem, space[i]), end="")
            i+=1
        print('')

        # Line
        self._printLine(space)

    def _printFramedWord(self, Word, width, centered=False, char='='):
        # |====|
        # |Word|
        # |====|
        a = '|%s|' % (char * len(Word))
        Word = '|%s|' % Word

        if centered:
            frmt = '{0:^{1}}'
        else:
            frmt = '{0:{1}}'
        print(frmt.format(a, width))
        print(frmt.format(Word, width))
        print(frmt.format(a, width))

    def _printValues(self, nest, dic, space, col, lines=True, printMain=False, notPipe=' '):
        # nest : if 0 then print row else if printMain then print KEY fi; _printValues(nest-1,...)
        # dic : dictionary that is json
        # space : width of element in row
        # col : width of row
        # printMain : True will print Keys in the center, False will omit them
        for author, info in dic.items():
            # Key, Main, author
            if nest == 0:
                # continue if value empty
                if info == {} or info == [] or info == "":
                    continue

                # pipe or not
                if lines or printMain==False: pipe = '|'
                else: pipe = notPipe

                # if id will be displayed
                i=0
                if printMain:
                    print('{0:{1}}'.format(pipe + str(author), space[i]), end="")
                    i+=1

                # print row
                for key in self._keylist:
                    print('{0:{1}}'.format(pipe + str(info[key]), space[i]), end="")
                    i+=1
                print("")

                if lines:
                    # Line
                    self._printLine(space,'-')
            else:
                self._printValues(nest - 1, info, space, col, lines, False,notPipe=notPipe)

    def _printLine(self,space,char='='):
        for i in space:
            print('|'+char*(i-1),end='')
        print('')


class VidsView(View):
    class exList(list):
        # list with items() like dictionary!
        def items(self):
            return ((i, self[i]) for i in range(len(self)) )
        def __str__(self):
            tmp = super().__str__()
            return ','.join(  tmp[2:-2].split("', '")  )

    def __init__(self, OrderList, Youtubers, Tags=None):
        super().__init__(OrderList)
        self._youtubers = Youtubers # id's of youtubers
        self._tags = Tags
        # path to youtubers folder
        self._folderPath = '{}{}'.format(getFullPathOfScript(),
                                         self._settings['paths']['youtubersFolder'])

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
            self._printFramedWord(name,len(name))

            # Print main content
            self._printValues(nest, self._source, space, col,
                           lines=lines,
                           printMain=printMain,
                              notPipe='|')

    def _getYTNames(self, path="raw/youtubers.txt") -> list:
        # Take youtuber names from id's
        self._loadFile(getFullPathOfScript()+path)
        res = []
        for y in self._youtubers:
            try:
                res.append( self._source[y]['channelName'] )
            except:
                res.append(y)
        return res

    def getFolderPath(self):
        return self._folderPath

    # returns list of space required to correctly print values
    def getSpace(self,ytNames, keyList, printMain) -> list:
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
                space[i].append(1+max(max(len(str(dic[key])) for dic in self._source ),len(key)))
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

    # returns a tuple (Nothing:bool, List:list)
    def __omitVidsWithoutTags(self,listDicts, Tags) -> (bool,list):
        Tags = set(Tags)
        tmp =  map( lambda dict:
             dict if Tags <= set(dict['tags'])
                and dict['show']
                and not dict['seen']
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


