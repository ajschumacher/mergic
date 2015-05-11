#!/usr/bin/env python

import re
import Levenshtein
import mergic


def initialize(name):
    initial = re.match("^[A-Z]", name).group()
    last = re.search("(?<=[ .])[A-Z].+$", name).group()
    return "{}. {}".format(initial, last)


def distance(x, y):
    x = initialize(x)
    y = initialize(y)
    return Levenshtein.distance(x, y)


blender = mergic.Blender(distance, 'append')
blender.script()
