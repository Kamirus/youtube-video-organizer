#!/usr/bin/env python3

import argparse
import json
import os
from editYoutubers import getFullPathOfScript


class View:
    # OrderList is a list with Keys that will be displayed
    def __init__(self, OrderList, path="raw/youtubers.txt"):
        self._path = getFullPathOfScript()+path
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
        except:
            raise ValueError("[ERROR]\ncannot load file")

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--id", help="Show list of youtubers with their id", action='store_true')
    parser.add_argument("-t","--table", help="Use table to show youtubers", action='store_true')
    parser.add_argument("-c", "--clear", help="Clear terminal before printing", action='store_true')

    args = parser.parse_args()

    if args.clear: os.system("clear")

    view = View(['channelName', 'publishedAfter'],)
    view.show(printMain=args.id,lines=args.table)
