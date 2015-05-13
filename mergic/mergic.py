#!/usr/bin/env python

import argparse
import sys
import json
import csv
from difflib import SequenceMatcher
from itertools import combinations
from collections import Counter
from collections import OrderedDict
from pprint import pprint


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


def _link_items(belongings, links):
    for one, other in links:
        if belongings[one] is belongings[other]:
            continue
        else:
            union = belongings[one] + belongings[other]
            for thing in union:
                belongings[thing] = union


def check(args):
    # With JSON there is a risk of duplicate keys;
    # the last one will win.
    data = json.loads(args.partition.read())
    n = _check(data)
    print "{} items in {} groups".format(n, len(data))


def diff(args):
    data1 = json.loads(args.first.read())
    _check(data1)
    data2 = json.loads(args.second.read())
    _check(data2)

    mixed_from = set()
    mixed_to = set()
    changes = dict()
    for key, values in data2.items():
        if data1.get(key) == values:
            del(data1[key])
        else:
            changes[key] = values
            mixed_to.update(values)
            to_find = mixed_to - mixed_from
            for key_from, values_from in data1.items():
                values_from = set(values_from)
                if to_find & values_from:
                    mixed_from.update(values_from)
                    del(data1[key_from])
            not_found = to_find - mixed_from
            if not_found:
                raise ValueError(not_found)
    if mixed_from != mixed_to:
        not_assigned = mixed_from - mixed_to
        raise ValueError(not_assigned)
    # TODO, possibly:
    # make the order that keys come out nicer
    print json.dumps(changes,
                     ensure_ascii=False,
                     indent=4,
                     separators=(',', ': ')).encode('utf-8')


def apply_diff(args):
    original = json.loads(args.partition.read())
    _check(original)
    changes = json.loads(args.patch.read())

    mixed_from = set()
    mixed_to = set()
    for key, values in changes.items():
        if original.get(key) == values:
            # this shouldn't happen, but still...
            del(original[key])
        else:
            mixed_to.update(values)
            to_find = mixed_to - mixed_from
            for key_from, values_from in original.items():
                values_from = set(values_from)
                if to_find & values_from:
                    mixed_from.update(values_from)
                    del(original[key_from])
            not_found = to_find - mixed_from
            if not_found:
                raise ValueError(not_found)
    if mixed_from != mixed_to:
        not_assigned = mixed_from - mixed_to
        raise ValueError(not_assigned)
    # TODO, possibly:
    # make the order that keys come out nicer
    original.update(changes)
    print json.dumps(original,
                     ensure_ascii=False,
                     indent=4,
                     separators=(',', ': ')).encode('utf-8')


def table(args):
    data = json.loads(args.partition.read())
    _check(data)
    writer = csv.writer(sys.stdout)
    writer.writerow(["original", "mergic"])
    for key, values in data.items():
        key = key.encode('utf-8')
        for value in values:
            value = value.encode('utf-8')
            writer.writerow([value, key])


class Blender():

    def __init__(self, distance='stock', key_method='longest'):
        if distance == 'stock':
            self.distance = lambda a, b: 1 - SequenceMatcher(None, a, b).ratio()
        else:
            self.distance = distance
        if key_method == 'longest':
            self.key_method = lambda x: max(sorted(x), key=len)
        elif key_method == 'append':
            self.key_method = lambda x: "|".join(x)
        else:
            self.key_method = key_method

    def make(self, args):
        items = [item.strip() for item in args.infile.readlines()]
        sets = {item: (item,) for item in items}

        links_at = {}
        for one, other in combinations(sets, 2):
            links_at.setdefault(self.distance(one, other), []).append((one, other))

        cutoffs = sorted(links_at)
        if args.cutoff is None:
            print "num groups, max group, num pairs, cutoff"
            print "----------------------------------------"
            print "{0: >10}, {1: >9}, {2: >9}, {3}".format(len(sets),
                                                                1, 0,
                                                                cutoffs[0] - 1)
        for cutoff in cutoffs:
            # alternative way to grow groups: on a per-group basis
            # rather than globally changing cutoff, could just grow
            # groups until they reach some "satisfactory" size
            _link_items(sets, links_at[cutoff])
            unique_sets = []
            for a_set in sets.values():
                if a_set not in unique_sets:
                    unique_sets.append(a_set)
            c = Counter(len(x) for x in unique_sets)
            if args.cutoff is None:
                print "{0: >10}, {1: >9}, {2: >9}, {3}".format(sum(c.values()),
                                                                    max(c.keys()),
                                                                    sum(len(x)*(len(x)-1)/2 for x in unique_sets),
                                                                    cutoff)
        if args.cutoff is None:
            return None

        ordered_items = sets.values()[0]

        # NOT DRY (copied from above)
        sets = {item: (item,) for item in items}
        for cutoff in [x for x in cutoffs if x <= args.cutoff]:
            _link_items(sets, links_at[cutoff])
        unique_sets = []
        for a_set in sets.values():
            if a_set not in unique_sets:
                unique_sets.append(a_set)
        unique_sets.sort(key=lambda x: (0-len(x), ordered_items.index(x[0])))
        result = OrderedDict()
        for item in unique_sets:
            result[self.key_method(item)] = list(item)

        print json.dumps(result, indent=4, separators=(',', ': '))

    def script(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()

        p_make = subparsers.add_parser('make',
                                       help='make a JSON partition from data')
        p_make.add_argument('infile',
                            nargs='?',
                            help='lines of text to make a partition for',
                            type=argparse.FileType('r'),
                            default=sys.stdin)
        p_make.add_argument('cutoff',
                            nargs='?',
                            help="cutoff for partition (if present)",
                            type=float)
        p_make.set_defaults(func=self.make)

        p_check = subparsers.add_parser('check',
                                        help='check validity of JSON partition')
        p_check.add_argument('partition',
                             nargs='?',
                             help='a JSON partition file',
                             type=argparse.FileType('r'),
                             default=sys.stdin)
        p_check.set_defaults(func=check)

        p_diff = subparsers.add_parser('diff',
                                       help='diff two JSON partitions')
        p_diff.add_argument('first',
                            help='a JSON partition file',
                            type=argparse.FileType('r'))
        p_diff.add_argument('second',
                            help='a JSON partition file',
                            type=argparse.FileType('r'))
        p_diff.set_defaults(func=diff)

        p_apply = subparsers.add_parser('apply',
                                        help='apply a patch to a JSON partition')
        p_apply.add_argument('partition',
                             help='a JSON partition file',
                             type=argparse.FileType('r'))
        p_apply.add_argument('patch',
                             help='a JSON partition patch file',
                             type=argparse.FileType('r'))
        p_apply.set_defaults(func=apply_diff)

        p_table = subparsers.add_parser('table',
                                        help='make merge table from JSON partition')
        p_table.add_argument('partition',
                             nargs='?',
                             help='a JSON partition file',
                             type=argparse.FileType('r'),
                             default=sys.stdin)
        p_table.set_defaults(func=table)

        args = parser.parse_args()
        args.func(args)


def script():
    blender = Blender()
    blender.script()

if __name__ == '__main__':
    script()
