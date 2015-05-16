#!/usr/bin/env python

import argparse
import sys
import json
import csv
import pickle
from difflib import SequenceMatcher
from itertools import combinations
from collections import Counter
from collections import OrderedDict


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


def _link_items(belongings, all_groups, links):
    """
    `belongings` is a dict from items to the group they're in
    `all_groups` is a set of all current groups
    `links` contains pairs of linked items
    """
    for one, other in links:
        if belongings[one] is belongings[other]:
            continue
        else:
            union = belongings[one] + belongings[other]
            all_groups.add(union)
            all_groups.remove(belongings[one])
            all_groups.remove(belongings[other])
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
        if set(data1.get(key, [])) == set(values):
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
        self.links_at = None
        self.ordered_items = None
        self.cutoffs = None

    def calc(self, args):
        try:
            with open('.mergic_cache', 'rb') as f:
                cache = pickle.load(f)
                (self.links_at, self.cutoffs, self.ordered_items) = cache
                items = self.ordered_items
        except IOError:
            items = [item.strip() for item in args.infile.readlines()]
            # build distance "matrix"
            links_at = {}
            for one, other in combinations(items, 2):
                links_at.setdefault(self.distance(one, other),
                                    []).append((one, other))
            self.links_at = links_at
            self.cutoffs = sorted(links_at.keys())
        links_at = self.links_at
        cutoffs = self.cutoffs
        group_for_item = {item: (item,) for item in items}
        all_groups = {(item,) for item in items}
        if args.command == 'calc':
            print "num groups, max group, num pairs, cutoff"
            print "----------------------------------------"
            data = (len(group_for_item), 1, 0, cutoffs[0] - 1)
            print "{0: >10}, {1: >9}, {2: >9}, {3}".format(*data)
        for cutoff in cutoffs:
            _link_items(group_for_item, all_groups, links_at[cutoff])
            c = Counter(len(x) for x in all_groups)
            if args.command == 'calc':
                data = (sum(c.values()),
                        max(c.keys()),
                        sum(len(x)*(len(x)-1)/2 for x in all_groups),
                        cutoff)
                print "{0: >10}, {1: >9}, {2: >9}, {3}".format(*data)
            if sum(c.values()) == 1:
                break
        self.ordered_items = group_for_item.values()[0]
        with open('.mergic_cache', 'wb') as f:
            pickle.dump((self.links_at, self.cutoffs, self.ordered_items),
                        f, protocol=2)

    def make(self, args):
        if self.links_at is None:
            self.calc(args)
        links_at = self.links_at
        # NOT DRY (copied from above)
        group_for_item = {item: (item,) for item in self.ordered_items}
        all_groups = {(item,) for item in self.ordered_items}
        for cutoff in [x for x in self.cutoffs if x <= args.cutoff]:
            _link_items(group_for_item, all_groups, links_at[cutoff])
        all_groups = list(all_groups)
        all_groups.sort(key=lambda x: (0-len(x), self.ordered_items.index(x[0])))
        result = OrderedDict()
        for item in all_groups:
            result[self.key_method(item)] = list(item)
        print json.dumps(result, indent=4, separators=(',', ': '))

    def script(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest='command')

        p_calc = subparsers.add_parser('calc',
                                       help='calculate all partitions of data')
        p_calc.add_argument('infile',
                            nargs='?',
                            help='lines of text to calculate groups for',
                            type=argparse.FileType('r'),
                            default=sys.stdin)
        p_calc.set_defaults(func=self.calc)

        p_make = subparsers.add_parser('make',
                                       help='make a JSON partition from data')
        p_make.add_argument('infile',
                            nargs='?',
                            help='lines of text to make a partition for',
                            type=argparse.FileType('r'),
                            default=sys.stdin)
        p_make.add_argument('cutoff',
                            help="cutoff for partition",
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
