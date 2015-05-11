# mergic: workflow support for reproducible deduplication and merging

With the mergic blender:

The distance calculation, cutoff evaluation, and partition creation are currently all in `mergic.py make`:

```bash
# see all the possible partitions by their statistics
./mergic.py make names_all.txt

# make a partition using a cutoff of 0.303
./mergic.py make 0.303 > partition.json
```

Edit the partition until it's good. Save it as `partition_edited.json`.

You can check that your partition is valid and see a cute summary:

```bash
./mergic.py check partition_edited.json
# 669 items in 354 groups
```

You could proceed directly, but there are also diffing tools! Generate a diff:

```bash
./mergic.py diff partition.json partition_edited.json > partition_diff.json
```

You can apply a diff to reconstruct an edited version:

```bash
./mergic.py apply partition.json partition_diff.json > partition_rebuilt.json
```

Now if you `mergic.py diff` the files `partition_edited.json` and `partition_rebuilt.json` the result should just be `{}` (no difference).

To generate a CSV merge table that you'll be able to use with any other tool:

```bash
./mergic.py table partition_edited.json > partition.csv
```

Now the file `partition.csv` has two columns, `original` and `mergic`, where `original` contains all the values that appeared in the original data and `mergic` contains the deduplicated keys. You can join this on to your original data and go to town.


## Distances

Here are some popular distances and how to do them with Python:

 * [Levenshtein string edit distance](http://en.wikipedia.org/wiki/Levenshtein_distance): The classic! It has many implementations; one of them is [python-Levenshtein](http://www.coli.uni-saarland.de/courses/LT1/2011/slides/Python-Levenshtein.html).

```python
# pip install python-Levenshtein
import Levenshtein
Levenshtein.distance("fuzzy", "wuzzy")
# 1
```

 * SeatGeek's [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy): As described in a [blog post](http://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/), some distance variants that people have found to work well in practice. Its responses are phrased as integer percent similarities; one way to make a distance is to subtract from 100.

```python
# pip install fuzzywuzzy
from fuzzywuzzy import fuzz
100 - fuzz.ratio("Levensthein", "Leviathan")
# 50
```

There are a ton of distances, even just within the two packages mentioned! You can also roll your own! (This is encouraged!)


## Old stuff

To produce the test data from its source:

```bash
./data.sh
## currently 669 unique names in names_all.txt
```

To make the best-guess merge table:

```bash
cat names_all.txt | ./uno.py > names_uno.txt
```

It looks like the only problem is with the Plíšková twins. But Karolína played in the [2013 US Open](http://en.wikipedia.org/wiki/2013_US_Open_%E2%80%93_Women%27s_Singles), so we only have to edit data rows two and three. The result is in `names_merge.txt`.

How many unique players are there?

```bash
tail +2 names_merge.txt | cut -d, -f2 | sort | uniq | wc -l
# 359
```

So who played the most in these events?

```bash
join -t, <(sort names_all.txt) <(sort names_merge.txt) | cut -d, -f2 | sort | uniq -c | sort -nr | head
#  24 Novak Djokovic
#  22 Rafael Nadal
#  21 Serena Williams
#  21 David Ferrer
#  20 Na Li
#  19 Victoria Azarenka
#  19 Agnieszka Radwanska
#  18 Stanislas Wawrinka
#  17 Tommy Robredo
#  17 Sloane Stephens
```

---

Thoughts so far:

 * Levenshtein distance is nice, but it turned out I could quickly get a "distance" with near-perfect behavior just on zero/nonzero grouping by writing a custom one.
     * This amounted to writing a function to extract a "key" which in the case of the tennis players was their first initial and a regex-determined "last name". Knowing this would work depended on looking at the data.
     * With a more usual distance metric, it would be nice to see a distribution of pairwise distances, which might suggest whether there are natural breakpoints.
 * It was easy to find one type of error by looking at groups that became too big.
     * It was nice to look at these as their groups rather than in some columnar format - the final output of a merge table is useful but not very readable.
     * To fix the issue I had to go back to the original site of the data and then find extra information from another source. Is there a way to make at least the first part easier?
     * It would probably be good to see a distribution of group sizes - "100 pairs, 20 singletons, 1 group of fifteen" etc.
 * It's hard to know if I missed errors in the smaller groups and singletons who didn't get matched.

 * Can I use tSNE (or similar) to get a visualization based just on a distance matrix?

Notes from doing the manual match for tennis (one hour):

```

Wozniacki! A Wozniak? C Wozniack?
 "C Wozniack" a typo for the Dane
 "A Wozniak" Canadian

Pliskova sisters
 but at least only Carolina was in the 2013 US Open

THE KUZNETSOVAS ><
 one American, one Russian, and they were both in Wimbledon
 ... as "A.Kuznetsov"
 but Andrey played twice
 so in "Wimbledon-men-2013.csv",
 "A.Kuznetsov,I.Sijsling," should be "Alex Kuznetsov,I.Sijsling,"

B.Becker is Benjamin, not Brian


cool! found the Juan Martin Del Potro fix! because they were near each other!

recognized Karolina Schmiedlova as long name that could partially match
```

For posterity: look how short this is!

```python
#!/usr/bin/env python

import sys
import re


def initialize(name):
    initial = re.match("^[A-Z]", name).group()
    last = re.search("(?<=[ .])[A-Z].+$", name).group()
    return "{}. {}".format(initial, last)


def main():
    items = {item.strip() for item in sys.stdin}
    groups = dict()
    for item in items:
        groups.setdefault(initialize(item), []).append(item)
    print "original,uno"
    for group in sorted(groups.values(), key=len, reverse=True):
        key = sorted(group, key=len)[-1]
        for item in group:
            print "{},{}".format(item, key)

if __name__ == '__main__':
    main()
```
