#!/usr/bin/env python

import sys
import json
import csv

text = sys.stdin.read()
data = json.loads(text)

writer = csv.writer(sys.stdout)
writer.writerow(["original", "unom"])

for key, values in data.items():
    for value in values:
        writer.writerow([value.encode('utf-8'), key.encode('utf-8')])
