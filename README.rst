======
mergic
======
-----------------------------------------------------------
workflow support for reproducible deduplication and merging
-----------------------------------------------------------

Say you have a bunch of strings, and some of them are different but refer to the same thing. Maybe it's just some long list, maybe it's the contents of two key columns from data sets that you'd like to merge.

::

    David Copperfield
    Lance Burton
    Dave Copperfield
    Levar Burton

Here's what you can do with ``mergic``:

Give ``mergic`` all your identifiers, one per line. If they are in a file called ``originals.txt``:

.. code:: bash

   mergic calc originals.txt

You will see output about the possible groupings ``mergic`` can produce based on its default distance function. (It's easy to use a custom distance function—see below.)

::

    num groups, max group, num pairs, cutoff
    ----------------------------------------
             4,         1,         0, -0.909090909091
             3,         2,         1, 0.0909090909091
             2,         2,         2, 0.25
             1,         4,         6, 0.714285714286

There are 4 groupings that ``mergic`` can make with the given distance function, ranging from a group for every name to a single group for all four names.

The ``num groups`` is the number of groups that ``mergic`` can make with the given ``cutoff``.

The ``max group`` is the number of items in the largest group for that grouping.

The ``num pairs`` column indicates the number of within-group links that correspond to the grouping. In some sense this represents how much work it is to check all the linkages that ``mergic`` is making. Thinking in groups is much better than thinking in individual pairwise comparisons, but the metric is useful for summarizing how much linking is happening.

The ``cutoff`` is the largest distance that still links individual items for a grouping.

Select a cutoff to produce the grouping you would like to see. If you would like to use the cutoff 0.3 and put the results in a file called ``grouping.json``:

.. code:: bash

   mergic make originals.txt 0.3 > grouping.json

Now ``grouping.json`` contains a grouping of your original data, specified in `JSON <http://www.json.org/>`__. It's designed to be human-readable, and human-editable, so you can check it and improve it as needed. The largest groups will be at the top, and similar items will be near one another.

::

    {
        "Lance Burton": [
            "Lance Burton",
            "Levar Burton"
        ],
        "David Copperfield": [
            "Dave Copperfield",
            "David Copperfield"
        ]
    }

There are two proposed groups, with proposed names "Lance Burton" and "David Copperfield". You probably want to copy the produced file and edit the copy.

.. code:: bash

   cp grouping.json grouping_fixed.json
   # edit `grouping_fixed.json`

You can edit the proposed group names—the keys of the object—if you like. The original values from the data are in the array values of the object, and you can move them around to correct the grouping. In this case you could also re-run ``mergic`` with a cutoff of 0.1 to get a correct grouping:

::

    {
        "David Copperfield": [
            "Dave Copperfield",
            "David Copperfield"
        ],
        "Lance Burton": [
            "Lance Burton"
        ],
        "Levar Burton": [
            "Levar Burton"
        ]
    }

Now that ``grouping_fixed.json`` is as perfect as it can be, you can move forward. You can also compare your two JSON grouping files and see what you changed. You can apply changes to a ``mergic``-produced file to recover your edited version. This way you have a complete and verifiable record of your work.

.. code:: bash

   mergic diff grouping.json grouping_fixed.json > diff.json
   mergic apply grouping.json diff.json > grouping_new.json
   mergic diff grouping_fixed.json grouping_new.json
   # {}  // (no changes)

The JSON grouping format is very convenient for humans, but for tabular data a merge table is more useful. A merge table has one column with the original values from your data and one column with the new keys. These are named ``original`` and ``mergic`` in the output:

.. code:: bash

   mergic table grouping_fixed.json > merge_table.csv

The file ``merge_table.csv`` looks like this:

::

    original,mergic
    Lance Burton,Lance Burton
    Levar Burton,Levar Burton
    Dave Copperfield,David Copperfield
    David Copperfield,David Copperfield

This merge table can now be used with any tabular data system. For merges, first merge it on to both tables and then merge by the ``mergic`` key. For deduplication, merge it on to the table(s) of interest and then use the ``mergic`` column as you would have used the original data.


Installation
============

.. code:: bash

   pip install mergic


Using a Custom Distance Function
================================

The ``mergic`` package provides a command-line script called ``mergic`` that uses Python's built-in ``difflib.SequenceMatcher.ratio()`` for calculating string distances, but a major strength of ``mergic`` is that it enables easy customization of the distance function via the ``mergic.Blender`` class. Making a custom ``mergic`` script is as easy as:

.. code:: python

   #!/usr/bin/env python
   # custom_mergic.py
   import mergic

   # Any custom distance you want to try! e.g.,
   def my_distance(a, b):
       return abs(len(a) - len(b))

   mergic.Blender(my_distance).script()

Now ``custom_mergic.py`` can be used just like the standard ``mergic`` script!

You can also use a custom function for generating the keys that values are de-duped to; by default ``mergic.Blender`` will use the first longest of a group's values in sorted order.


Distances You Might Like
------------------------

`Levenshtein string edit distance <http://en.wikipedia.org/wiki/Levenshtein_distance>`__: The classic! It has many implementations; one of them is `python-Levenshtein <http://www.coli.uni-saarland.de/courses/LT1/2011/slides/Python-Levenshtein.html>`__.

.. code:: python

    # pip install python-Levenshtein
    import Levenshtein
    Levenshtein.distance("fuzzy", "wuzzy")
    # 1

SeatGeek's `fuzzywuzzy <https://github.com/seatgeek/fuzzywuzzy>`__: As described in their `blog post <http://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/>`__, some people have found these variants to work well in practice. Responses from ``fuzzywuzzy`` are phrased as integer percent similarities; one way to make a distance is to subtract from 100.

.. code:: python

    # pip install fuzzywuzzy
    from fuzzywuzzy import fuzz
    100 - fuzz.ratio("Levensthein", "Leviathan")
    # 50

There are a ton of distances, even just within the two packages mentioned!

You can also make your own!
