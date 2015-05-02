#!/usr/bin/env python

import sys
import re


def initialize(name):
    initial = re.match("^[A-Z]", name).group()
    last = re.search("(?<=[ .])[A-Z].+$", name).group()
    return "{}. {}".format(initial, last)


def main():
    items = {item.strip() for item in sys.stdin}
    groups = dict()
    for item in items:
        groups.setdefault(initialize(item), []).append(item)
    print "original,uno"
    for group in sorted(groups.values(), key=len, reverse=True):
        key = sorted(group, key=len)[-1]
        for item in group:
            print "{},{}".format(item, key)

if __name__ == '__main__':
    main()
