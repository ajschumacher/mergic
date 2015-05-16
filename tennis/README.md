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


Make sure you don't already have a `names.txt` file, and then produce one with all the names that appear.

```bash
for filename in *.csv
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

Notes from doing the manual match for tennis (one hour):

```
Wozniacki! A Wozniak? C Wozniack?
 "C Wozniack" a typo for the Dane
 "A Wozniak" Canadian


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


.. code:: bash

    mergic check partition_edited.json
    # 669 items in 354 groups

You could proceed directly, but there are also diffing tools! Generate a
diff:

.. code:: bash

    mergic diff partition.json partition_edited.json > partition_diff.json

You can apply a diff to reconstruct an edited version:

.. code:: bash

    mergic apply partition.json partition_diff.json > partition_rebuilt.json

Now if you ``mergic diff`` the files ``partition_edited.json`` and
``partition_rebuilt.json`` the result should just be ``{}`` (no
difference).

To generate a CSV merge table that you'll be able to use with any other
tool:

.. code:: bash

    mergic table partition_edited.json > partition.csv

Now the file ``partition.csv`` has two columns, ``original`` and
``mergic``, where ``original`` contains all the values that appeared in
the original data and ``mergic`` contains the deduplicated keys. You can
join this on to your original data and go to town.
