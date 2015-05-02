#!/usr/bin/env python

import sys
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
    print Levenshtein.distance(sys.argv[1], sys.argv[2])
    print 'is', sys.argv[1], 'also', sys.argv[2], '?',
    response = getch()
    print response

if __name__ == '__main__':
    main()
