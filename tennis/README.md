## Old stuff from tennis

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


This write-up was pretty specific to the tennis data:

The distance calculation, cutoff evaluation, and partition creation are
currently all in ``mergic make``:

.. code:: bash

    # see all the possible partitions by their statistics
    mergic make names_all.txt

    # make a partition using a cutoff of 0.303
    mergic make 0.303 > partition.json

Edit the partition until it's good. Save it as
``partition_edited.json``.

You can check that your partition is valid and see a cute summary:

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
