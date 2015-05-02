#!/usr/bin/env python

import sys
import Levenshtein


def main():
    print Levenshtein.distance(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()
