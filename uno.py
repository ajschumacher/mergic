#!/usr/bin/env python

import sys
from itertools import combinations
import Levenshtein


def _find_getch():
    # courtesy of Louis
    # http://stackoverflow.com/questions/510357/
    try:
        import termios
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return msvcrt.getch

    # POSIX system. Create and return a getch that manipulates the tty.
    import sys, tty
    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch

getch = _find_getch()


def main():
    items = {item.strip() for item in sys.stdin}
    dist_items = [(Levenshtein.distance(first, second), first, second)
                  for first, second
                  in combinations(items, 2)]
    dist_items.sort()
    for row in dist_items:
        print row

if __name__ == '__main__':
    main()
