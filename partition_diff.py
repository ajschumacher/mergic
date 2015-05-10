#!/usr/bin/env python

import sys
import json


with open(sys.argv[1]) as f:
    text1 = f.read()

with open(sys.argv[2]) as f:
    text2 = f.read()

data1 = json.loads(text1)
data2 = json.loads(text2)

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
