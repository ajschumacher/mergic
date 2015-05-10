#!/usr/bin/env python

import sys
import json


with open(sys.argv[1]) as f:
    original = json.loads(f.read())

with open(sys.argv[2]) as f:
    changes = json.loads(f.read())


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
