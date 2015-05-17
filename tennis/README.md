# `mergic` with a custom distance function


Download the [Tennis Major Tournament Match Statistics Data Set](https://archive.ics.uci.edu/ml/datasets/Tennis+Major+Tournament+Match+Statistics) from the [UC Irvine Machine Learning Repository](https://archive.ics.uci.edu/ml/) into an empty directory:

```bash
wget https://archive.ics.uci.edu/ml/machine-learning-databases/00300/Tennis-Major-Tournaments-Match-Statistics.zip
```

This file should be stable, but it's also included [here](Tennis-Major-Tournaments-Match-Statistics.zip) and/or you can verify that its `md5` is `e9238389e4de42ecf2daf425532ce230`.


Unpack eight CSV files from the `Tennis-Major-Tournaments-Match-Statistics.zip`:

```bash
unzip Tennis-Major-Tournaments-Match-Statistics.zip
```


You should see that the first two columns of each file contain player names, though the column names are not consistent. For example:

```bash
head -2 AusOpen-women-2013.csv | cut -c 1-40
```

```text
Player1,Player2,Round,Result,FNL1,FNL2,F
Serena Williams,Ashleigh Barty,1,1,2,0,5
```

```bash
head -2 USOpen-women-2013.csv | cut -c 1-40
```

```text
Player 1,Player 2,ROUND,Result,FNL.1,FNL
S Williams,V Azarenka,7,1,2,1,57,44,43,2
```


Make a `names.txt` with all the names that appear:

```bash
for filename in *2013.csv
do
    for field in 1 2
    do
        tail +2 $filename | cut -d, -f$field >> names.txt
    done
done
```


Now you have a file with 1,886 lines, each one of 669 unique strings, as you can verify:

```bash
wc -l names.txt
sort names.txt | uniq | wc -l
```

There are too many unique strings—sometimes more than one string for the same player. As a result, a count of the most common names will not accurately tell us who played the most in these 2013 tennis competitions.


```bash
sort names.txt | uniq -c | sort -nr | head
```

```text
  21 Rafael Nadal
  17 Stanislas Wawrinka
  17 Novak Djokovic
  17 David Ferrer
  15 Roger Federer
  14 Tommy Robredo
  13 Richard Gasquet
  11 Victoria Azarenka
  11 Tomas Berdych
  11 Serena Williams
```

The list above is not the answer we’re looking for. We want to be correct.


In the tennis data, names appear sometimes with full first names and sometimes with only first initials. To get good comparisons, we should:

 * Transform all the data to the same format, as nearly as possible.
 * Use a good distance on the transformed data.

We can do both of these things in our custom script, [tennis_mergic.py](tennis_mergic.py). It only [requires](requirements.txt) the `mergic` and `python-Levenshtein` packages.

```python
#!/usr/bin/env python

import re
import Levenshtein
import mergic


def first_initial_last(name):
    initial = re.match("^[A-Z]", name).group()
    last = re.search("(?<=[ .])[A-Z].+$", name).group()
    return "{}. {}".format(initial, last)


def distance(x, y):
    x = first_initial_last(x)
    y = first_initial_last(y)
    return Levenshtein.distance(x, y)


mergic.Blender(distance).script()
```


Now [tennis_mergic.py](tennis_mergic.py) can be used just like the standard `mergic` script.

```bash
./tennis_mergic.py calc names.txt
```

```text
num groups, max group, num pairs, cutoff
----------------------------------------
       669,         1,         0, -1
       358,         5,       384, 0
       348,         6,       414, 1
       332,         6,       470, 2
       262,        85,      5117, 3
       165,       324,     52611, 4
        86,       496,    122899, 5
        46,       584,    170287, 6
        24,       624,    194407, 7
        16,       641,    205138, 8
        10,       650,    210940, 9
         4,       663,    219459, 10
         2,       668,    222778, 11
         1,       669,    223446, 12
```

There is a clear best cutoff here, as the size of the max group jumps from 6 items to 85 and the number of within-group comparisons jumps from 470 to 5,117. So we create a partition where the Levenshtein distance between names in our standard first initial and last name format is no more than two, and put the result in a file called `groups.json`:

```bash
./tennis_mergic.py make names.txt 2 > groups.json
```

As expected, the proposed grouping has combined things over-zealously in some places:

```bash
head -5 groups.json
```

```json
{
    "Yen-Hsun Lu": [
        "Di Wu",
        "Yen-Hsun Lu",
        "Y-H.Lu",
```


Manual editing can produce a corrected version of the original grouping, which could be saved as `edited.json`:

```bash
head -8 edited.json
```

```json
{
    "Yen-Hsun Lu": [
        "Yen-Hsun Lu",
        "Y-H.Lu"
    ],
    "Di Wu": [
        "Di Wu"
    ],
```

Parts of the review process would be difficult or impossible for a computer to do accurately.

 * There are the Plíšková twins, Karolína and Kristýna. When we see that `K Pliskova` appears, we have to go back and see that this occurred in the `USOpen-women-2013.csv` file, and only Karolína played in the [2013 US Open](http://en.wikipedia.org/wiki/2013_US_Open_%E2%80%93_Women%27s_Singles).
 * In a similar but less interesting way, `B.Becker` turns out to refer to Benjamin, not Brian.
 * An `A Wozniak` appears with `C Wozniack` and `C Wozniacki`. The first initial does turn out to differentiate the Canadian from the Dane.
 * The name `A.Kuznetsov` refers to *both* Andrey *and* Alex in `Wimbledon-men-2013.csv`. This can't be resolved by `mergic`. One way to resolve the issues is to edit `Wimbledon-men-2013.csv` so that `A.Kuznetsov,I.Sijsling` becomes `Alex Kuznetsov,I.Sijsling`, based on checking [records from that competition](http://en.wikipedia.org/wiki/2013_Wimbledon_Championships_%E2%80%93_Men%27s_Singles).
 * `Juan Martin Del Potro` is unfortunately too different from `J.Del Potro` in the current formulation to be grouped automatically, but a human reviewer can correct this. Similarly for `Anna Schmiedlova` and `Anna Karolina Schmiedlova`.


After editing, you can check that the new grouping is still valid. At this stage we aren't using anything custom any more, so the default `mergic` is fine:

```bash
mergic check partition_edited.json
```

```text
669 items in 354 groups
```

The `mergic` diffing tools make it easy to make comparisons that would otherwise be difficult, letting us focus on and save only changes that are human reviewers make rather than whole files.


```bash
mergic diff groups.json edited.json > diff.json
```

Now `diff.json` only has the entries that represent changes from the original `groups.json`.

The edited version can be reconstructed from the original and the diff with `mergic apply`:

```bash
mergic apply groups.json diff.json > rebuilt.json
```

The order of `rebuilt.json` may not be identical to the original `edited.json`, but the diff will be empty, meaning the file is equivalent:

```bash
mergic diff edited.json rebuilt.json
```

```json
{}
```

Finally, to generate a CSV merge table that you'll be able to use with any other tool:

```bash
mergic table edited.json > merge.csv
```

Now the file `merge.csv` has two columns, `original` and `mergic`, where `original` contains all the values that appeared in the original data and `mergic` contains the deduplicated keys. You can join this on to your original data and go to town.

Here's how we might do that to quickly get a list of who played the most in these 2013 tennis events:

```bash
join -t, <(sort names.txt) <(sort merge.csv) | cut -d, -f2 | sort | uniq -c | sort -nr | head
```

```text
  24 Novak Djokovic
  22 Rafael Nadal
  21 Serena Williams
  21 David Ferrer
  20 Na Li
  19 Victoria Azarenka
  19 Agnieszka Radwanska
  18 Stanislas Wawrinka
  17 Tommy Robredo
  17 Sloane Stephens
```

Note that this is not the same as the result we got before resolving these name issues:

```bash
sort names.txt | uniq -c | sort -nr | head
```

```text
  21 Rafael Nadal
  17 Stanislas Wawrinka
  17 Novak Djokovic
  17 David Ferrer
  15 Roger Federer
  14 Tommy Robredo
  13 Richard Gasquet
  11 Victoria Azarenka
  11 Tomas Berdych
  11 Serena Williams
```

As it happens, using a cutoff of 0 and doing no hand editing will still give the correct top ten. In general the desired result and desired level of certainty in its correctness will inform the level of effort that is justified.
