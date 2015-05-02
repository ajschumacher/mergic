#!/usr/bin/env python

import sys
from itertools import combinations
import re
import Levenshtein


def initialize(name):
    initial = re.match("^[A-Z]", name).group()
    last = re.search("(?<=[ .])[A-Z].+$", name).group()
    return "{}. {}".format(initial, last)


def main():
    items = {item.strip() for item in sys.stdin}
    dist_items = [(Levenshtein.distance(initialize(first),
                                        initialize(second)),
                   first,
                   second)
                  for first, second
                  in combinations(items, 2)]
    dist_items.sort()
    for row in dist_items:
        print row

if __name__ == '__main__':
    main()
