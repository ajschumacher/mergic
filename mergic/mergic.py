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


# Naming convention:
# A leading underscore means the function takes "self"
# A trailing underscore means the function takes parser "args"


def print_json(thing):
    """Print a Python data structure as formatted JSON."""
    print json.dumps(thing,
                     ensure_ascii=False,
                     indent=4,
                     separators=(',', ': ')).encode('utf-8')


def check(partition):
    """Confirm the passed dict is a partition.

    Parameters
    ----------
    partition : dict
        A partition dictionary where the values are lists. Items appear
        exactly once through all the value lists (they are "assigned to"
        their key value.)

    Returns
    -------
    int
        The number of items partitioned by the partition.

    Raises
    ------
    ValueError
        If a value appears more than once in one value list
        or a value appears in more than one value list.

    """
    all_items = set()
    for values in partition.values():
        value_set = set(values)
        if len(values) != len(value_set):
            raise ValueError('Duplication in {}'.format(values))
        already_seen = list(all_items & value_set)
        if len(already_seen) != 0:
            raise ValueError('{} in more than one group'.format(already_seen))
        all_items.update(values)
    return len(all_items)


def check_(args):
    """Check a partition loaded from a file at the command line."""
    data = json.loads(args.partition.read())
    n = check(data)
    print "{} items in {} groups".format(n, len(data))


def link_items(group_of, links):
    """Put items that are linked into the same group.

    Parameters
    ----------
    group_of : dict
        Keys are items being partitioned and values are tuples representing
        the group that the key is currently assigned to. Usually starts as
        every item pointing to a tuple containing only the item itself.
    links : list
        Contains tuples (pairs) representing items to link.

    """
    for one, other in links:
        if group_of[one] is group_of[other]:
            continue
        else:
            union = group_of[one] + group_of[other]
            for thing in union:
                group_of[thing] = union


def diff(first, second):
    """Generate the differences from a first to a second partition.

    Parameters
    ----------
    first  : dict
    second : dict
        Partition dictionaries where the values are lists. In each,
        items appear exactly once through all the value lists (they
        are "assigned to" their key value.)

    Returns
    -------
    dict
        A "patch" partition, for the set of values that are assigned
        differently in the second partition than the first. It can be
        applied to the first partition to generate the second.

    Raises
    ------
    ValueError
        If a value in the first partition is not assigned anywhere in
        the second partition or if the second partition assigns a
        value not found in the first partition.

    """
    mixed_from = set()
    mixed_to = set()
    patch = dict()
    for key, values in second.items():
        if set(first.get(key, [])) == set(values):
            del(first[key])
        else:
            patch[key] = values
            mixed_to.update(values)
            to_find = mixed_to - mixed_from
            for key_from, values_from in first.items():
                values_from = set(values_from)
                if to_find & values_from:
                    mixed_from.update(values_from)
                    del(first[key_from])
            not_found = to_find - mixed_from
            if not_found:
                raise ValueError(not_found)
    if mixed_from != mixed_to:
        not_assigned = mixed_from - mixed_to
        raise ValueError(not_assigned)
    return patch


def diff_(args):
    """Check and diff two partitions loaded from files at the command line."""
    first = json.loads(args.first.read())
    check(first)
    second = json.loads(args.second.read())
    check(second)
    patch = diff(first, second)
    print_json(patch)


def equal(first, second):
    """Check a first and second partition for equality.

    Parameters
    ----------
    first  : dict
    second : dict
        Partition dictionaries where the values are lists. In each,
        items appear exactly once through all the value lists (they
        are "assigned to" their key value.)

    Returns
    -------
    boolean
        True if the difference is empty, otherwise False.

    """
    try:
        patch = diff(first, second)
        if patch == {}:
            return True
    except ValueError:
        pass
    return False


def apply_diff(partition, patch):
    """Apply a patch to a partition (in place).

    Parameters
    ----------
    partition : dict
        A partition dictionary where the values are lists. Items appear
        exactly once through all the value lists (they are "assigned to"
        their key value.)

    patch : dict
        A "patch" partition, for the set of values that should be
        assigned differently from how they are in the original
        partition.

    Returns
    -------
    None
        The `partition` passed is modified in place.

    """
    mixed_from = set()
    mixed_to = set()
    for key, values in patch.items():
        if partition.get(key) == values:
            # this shouldn't happen, but still...
            del(partition[key])
        else:
            mixed_to.update(values)
            to_find = mixed_to - mixed_from
            for key_from, values_from in partition.items():
                values_from = set(values_from)
                if to_find & values_from:
                    mixed_from.update(values_from)
                    del(partition[key_from])
            not_found = to_find - mixed_from
            if not_found:
                raise ValueError(not_found)
    if mixed_from != mixed_to:
        not_assigned = mixed_from - mixed_to
        raise ValueError(not_assigned)
    partition.update(patch)


def apply_diff_(args):
    """Apply a patch to a partition, at the command line."""
    partition = json.loads(args.partition.read())
    check(partition)
    patch = json.loads(args.patch.read())
    apply_diff(partition, patch)
    print_json(partition)


def table(partition):
    """Generate 'merge table' rows from a partition.

    Parameters
    ----------
    partition : dict
        A partition dictionary where the values are lists. Items appear
        exactly once through all the value lists (they are "assigned to"
        their key value.)

    Yields
    ------
    tuple
        Pairs of original and new names, as specified in the partition,
        encoded in UTF-8.

    """
    for key, values in partition.items():
        for value in values:
            yield (value, key)


def table_(args):
    """Print out a two-column 'merge table' at the command line."""
    partition = json.loads(args.partition.read())
    check(partition)
    writer = csv.writer(sys.stdout)
    writer.writerow(["original", "mergic"])
    for row in table(partition):
        row = [str(element).encode('utf-8') for element in row]
        writer.writerow(row)


def _calc_(self, args):
    """Calculate possible groupings and print out a summary."""
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
    if args.command == 'calc':
        print "num groups, max group, num pairs, cutoff"
        print "----------------------------------------"
        data = (len(group_for_item), 1, 0, cutoffs[0] - 1)
        print "{0: >10}, {1: >9}, {2: >9}, {3}".format(*data)
    for cutoff in cutoffs:
        link_items(group_for_item, links_at[cutoff])
        all_groups = set(group_for_item.values())
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


def _make_(self, args):
    """Generate and print out a partition at a cutoff."""
    if self.links_at is None:
        self.calc(args)
    links_at = self.links_at
    # NOT DRY (copied from above)
    group_for_item = {item: (item,) for item in self.ordered_items}
    for cutoff in [x for x in self.cutoffs if x <= args.cutoff]:
        link_items(group_for_item, links_at[cutoff])
    all_groups = list(set(group_for_item.values()))
    all_groups.sort(key=lambda x: (0-len(x), self.ordered_items.index(x[0])))
    result = OrderedDict()
    for item in all_groups:
        result[self.key_method(item)] = list(item)
    print_json(result)


def _script(self):
    """Parse command-line arguments and expose functionality."""
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
    p_check.set_defaults(func=check_)

    p_diff = subparsers.add_parser('diff',
                                   help='diff two JSON partitions')
    p_diff.add_argument('first',
                        help='a JSON partition file',
                        type=argparse.FileType('r'))
    p_diff.add_argument('second',
                        help='a JSON partition file',
                        type=argparse.FileType('r'))
    p_diff.set_defaults(func=diff_)

    p_apply = subparsers.add_parser('apply',
                                    help='apply a patch to a JSON partition')
    p_apply.add_argument('partition',
                         help='a JSON partition file',
                         type=argparse.FileType('r'))
    p_apply.add_argument('patch',
                         help='a JSON partition patch file',
                         type=argparse.FileType('r'))
    p_apply.set_defaults(func=apply_diff_)

    p_table_help = 'make a merge table from a JSON partition'
    p_table = subparsers.add_parser('table', help=p_table_help)
    p_table.add_argument('partition',
                         nargs='?',
                         help='a JSON partition file',
                         type=argparse.FileType('r'),
                         default=sys.stdin)
    p_table.set_defaults(func=table_)

    args = parser.parse_args()
    args.func(args)


class Blender():

    def __init__(self, distance='stock', key_method='longest'):
        if distance == 'stock':
            distance = lambda a, b: 1 - SequenceMatcher(None, a, b).ratio()
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

    calc = _calc_
    make = _make_
    script = _script


def script():
    """Run a default mergic Blender at the command line."""
    blender = Blender()
    blender.script()

if __name__ == '__main__':
    script()
