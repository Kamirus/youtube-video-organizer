#!/usr/bin/env python3

import argparse
import os

from View import View

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--id", help="Show list of youtubers with their id", action='store_true')
    parser.add_argument("-t","--table", help="Use table to show youtubers", action='store_true')
    parser.add_argument("-c", "--clear", help="Clear terminal before printing", action='store_true')

    args = parser.parse_args()

    if args.clear: os.system("clear")

    view = View(['channelName', 'publishedAfter'],)
    try:
        view.show(printMain=args.id,lines=args.table)
    except Exception as e:
        print("[ERROR] = %s" % e)
