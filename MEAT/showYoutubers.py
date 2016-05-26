#!/usr/bin/env python3

import argparse
import json
import os


class View:
    # OrderList is a list with Keys that will be displayed
    def __init__(self, OrderList, path="raw/youtubers.txt"):
        self.__path = path
        self.__source = None
        self.__keylist = OrderList

        # Fill source with json file
        try:
            file = open(self.__path, 'r')
            self.__source = json.load(file)
            # self.__source = json.loads('%s' % file.read())
            file.close()
        except:
            raise ValueError("[ERROR]\ncannot load file with youtubers")

    def show(self, nest=0,
             lines=False, printMain=False, framed=False, headingChar='='):
        # Number of columns
        col = os.get_terminal_size().columns

        # Width for one element in a row
        space = col // len(self.__keylist)

        # Make a nice heading with key
        self.__heading(space, headingChar)

        # Print main content
        self.__printValues(nest, self.__source, space, col,
                           lines,
                           printMain,
                           framed)

    def __heading(self, space, char='='):
        line = '|' + char * (space - 1)
        l = len(self.__keylist)

        # Line
        print(line * l)

        # key
        for elem in self.__keylist:
            print('{0:{1}}'.format('|' + elem, space), end="")

        # Line
        print(line * l)

    def __printFramedWord(self, Word, width, centered=False, char='='):
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

    def __printValues(self, nest, dic, space, col, lines=True, printMain=False, framed=False):
        # nest : if 0 then print row else if printMain then print KEY fi; __printValues(nest-1,...)
        # dic : dictionary that is json
        # space : width of element in row
        # col : width of row
        # printMain : True will print Keys in the center, False will omit them
        for author, info in dic.items():
            # Key, Main, author
            if printMain:
                print('')
                if framed:
                    self.__printFramedWord(author, col, char='-')
                else:
                    print('id = %s' % author)

            if nest == 0:
                if lines or printMain==False: pipe = '|'
                else: pipe = ''

                line = '|' + '-' * (space - 1)
                l = len(self.__keylist)

                if lines:
                    # Line
                    print(line * l)

                for i in self.__keylist:
                    print('{0:{1}}'.format(pipe + info[i], space), end="")
                print("")

                if lines:
                    # Line
                    print(line * l)
            else:
                self.__printValues(nest - 1, info, space, col, lines, False, False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--id", help="Show list of youtubers with their id", action='store_true')
    parser.add_argument("-t","--table", help="Use table to show youtubers", action='store_true')
    parser.add_argument("-c", "--clear", help="Clear terminal before printing", action='store_true')

    args = parser.parse_args()

    if args.clear: os.system("clear")

    if args.id:
        view = View(['channelName', 'publishedAfter'])
        view.show( printMain=True)
    elif args.table:
        view = View(['channelName', 'publishedAfter'])
        view.show(lines=True)
    else:
        view = View(['channelName', 'publishedAfter'])
        view.show()
