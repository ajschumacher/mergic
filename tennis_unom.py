#!/usr/bin/env python

import re
import Levenshtein
from unom import Unom


def initialize(name):
    initial = re.match("^[A-Z]", name).group()
    last = re.search("(?<=[ .])[A-Z].+$", name).group()
    return "{}. {}".format(initial, last)

distance = lambda x, y: Levenshtein.distance(initialize(x), initialize(y))


# TODO: actually use `distance`
nom = Unom()
nom.script()
