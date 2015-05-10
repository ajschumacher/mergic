#!/usr/bin/env python

import sys
import json

text = sys.stdin.read()
data = json.loads(text)

# there is a risk of duplicate keys;
# the last one will win

# check that the values never repeat
total = set()
for values in data.values():
    # not repeated in this list
    assert len(values) == len(set(values))
    # not repeated from earlier
    assert total.intersection(values) == set()
    # now add to running list
    total.update(values)

print "{} items in {} groups".format(len(total),
                                     len(data))
