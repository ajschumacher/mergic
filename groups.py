import Levenshtein
from fuzzywuzzy import fuzz
from itertools import combinations
from collections import Counter
from uno import initialize


data_file_name = 'names_all.txt'
# data_file_name = 'RLdata500.csv'
with open(data_file_name) as f:
    sets = {name.strip(): (name.strip(),) for name in f.readlines()}

# sets = {a: {a} for a in ['aa', 'ab', 'ac', 'ad']}


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
# store: (cutoff, {size: number_of_em}
tables = {cutoffs[0] - 1: Counter(len(x) for x in sets.values())}
for cutoff in cutoffs:
    # alternative way to grow groups: on a per-group basis
    # rather than globally changing cutoff, could just grow
    # groups until they reach some "satisfactory" size
    for one, other in links_at[cutoff]:
        if sets[one] is sets[other]:
            continue
        else:
            union = sets[one] + sets[other]
            for thing in union:
                sets[thing] = union
    unique_sets = []
    for a_set in sets.values():
        if a_set not in unique_sets:
            unique_sets.append(a_set)
    tables[cutoff] = (Counter(len(x) for x in unique_sets),
                      sum(len(x)*(len(x)-1)/2 for x in unique_sets))
