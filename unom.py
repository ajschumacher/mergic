#!/usr/bin/env python

import argparse
import sys
import json


def _check(partition):
    """Confirm the passed dict is a partition.

    A partition is valid if no entries from the value lists
    are ever repeated.

    Raise an exception if there's a problem,
    otherwise return the total number of entries."""
    all_items = set()
    for values in partition.values():
        # not repeated in this list
        assert len(values) == len(set(values))
        # not repeated from earlier
        assert all_items.intersection(values) == set()
        # now add to running list
        all_items.update(values)
    return len(all_items)


def check(args):
    # With JSON there is a risk of duplicate keys;
    # the last one will win.
    data = json.loads(args.infile.read())
    n = _check(data)
    print "{} items in {} groups".format(n, len(data))


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

p_verify = subparsers.add_parser('check',
                                 help='check validiy of JSON partition')
p_verify.add_argument('infile', nargs='?',
                      type=argparse.FileType('r'),
                      default=sys.stdin)
p_verify.set_defaults(func=check)

args = parser.parse_args()
args.func(args)
