import json
import Levenshtein
from fuzzywuzzy import fuzz
from itertools import combinations
from collections import Counter
from collections import OrderedDict
from uno import initialize

data_file_name = 'names_all.txt'
# data_file_name = 'RLdata500.csv'


def link_items(belongings, links):
    for one, other in links:
        if belongings[one] is belongings[other]:
            continue
        else:
            union = belongings[one] + belongings[other]
            for thing in union:
                belongings[thing] = union

with open(data_file_name) as f:
    sets = {name.strip(): (name.strip(),) for name in f.readlines()}

# distance = Levenshtein.distance
# distance = lambda x, y: 100 - fuzz.ratio(x, y)
# distance = lambda x, y: 100 - fuzz.partial_ratio(x, y)
# distance = lambda x, y: 100 - fuzz.token_sort_ratio(x, y)
# distance = lambda x, y: 100 - fuzz.token_set_ratio(x, y)
distance = lambda x, y: Levenshtein.distance(initialize(x), initialize(y))
links_at = {}
for one, other in combinations(sets, 2):
    links_at.setdefault(distance(one, other), []).append((one, other))

cutoffs = sorted(links_at)
tables = {cutoffs[0] - 1: {1: len(sets)}}
# TODO: stop search after using all items
for cutoff in cutoffs:
    # alternative way to grow groups: on a per-group basis
    # rather than globally changing cutoff, could just grow
    # groups until they reach some "satisfactory" size
    link_items(sets, links_at[cutoff])
    unique_sets = []
    for a_set in sets.values():
        if a_set not in unique_sets:
            unique_sets.append(a_set)
    tables[cutoff] = (Counter(len(x) for x in unique_sets),
                      sum(len(x)*(len(x)-1)/2 for x in unique_sets))
ordered_items = sets.values()[0]

# NOT DRY (copied from above)
with open(data_file_name) as f:
    sets = {name.strip(): (name.strip(),) for name in f.readlines()}
for cutoff in [x for x in cutoffs if x <= 2]:
    link_items(sets, links_at[cutoff])
unique_sets = []
for a_set in sets.values():
    if a_set not in unique_sets:
        unique_sets.append(a_set)
unique_sets.sort(key=lambda x: (0-len(x), ordered_items.index(x[0])))
result = OrderedDict()
for item in unique_sets:
    result[max(item, key=len)] = list(item)

print json.dumps(result, indent=4, separators=(',', ': '))
