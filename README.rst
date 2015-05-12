======
mergic
======
-----------------------------------------------------------
workflow support for reproducible deduplication and merging
-----------------------------------------------------------

Use ``mergic`` when you need to merge data by key identifiers that don't quite all match. Use ``mergic`` when you need to resolve duplicates that aren't perfect duplicates.

Use ``mergic`` when you want your process to be reproducible—even when it requires some human judgment. Use ``mergic`` when human review is required, but the humans don't want to go insane.

Give ``mergic`` all your identifiers, one per line. If they are in a file called ``column.txt``:

.. code:: bash

   mergic make column.txt

You will see output about the possible groupings ``mergic`` can produce based on its default distance function. (It's easy to use a custom distance function—see below.) Select a cutoff to produce the grouping you would like to see. If you would like to use the cutoff 0.5 and put the results in a file called ``grouping.json``:

.. code:: bash

   mergic make column.txt 0.5 > grouping.json

Now ``grouping.json`` contains a grouping of your original data in JSON format. It's designed to be human-readable, and human-editable, so you can check it and improve it as needed. The largest groups will be at the top, and similar items will be near one another. You can copy the produced file and edit the copy:

.. code:: bash

   cp grouping.json grouping_fixed.json
   # edit `grouping_fixed.json`

Now that `grouping_fixed.json` is as perfect as it can be, you can move forward. You can also compare your two JSON grouping files and see what you changed. You can apply changes to a ``mergic``-produced file to recover your edited version. This way you have a complete and verifiable record of your work.

.. code:: bash

   mergic diff grouping.json grouping_fixed.json > diff.json
   mergic apply grouping.json diff.json > grouping_new.json
   mergic diff grouping_fixed.json grouping_new.json
   # {}  // (no changes)

The JSON grouping format is very convenient for humans, but for tabular data a merge table is more useful. A merge table has one column with the original values from your data and one column with the new reduced keys. These are named ``original`` and ``mergic`` in the output:

.. code:: bash

   mergic table grouping_fixed.json > merge_table.csv

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

Here are some popular distances with Python implementations:

`Levenshtein string edit distance <http://en.wikipedia.org/wiki/Levenshtein_distance>`__: The classic! It has many implementations; one of them is `python-Levenshtein <http://www.coli.uni-saarland.de/courses/LT1/2011/slides/Python-Levenshtein.html>`__.

.. code:: python

    # pip install python-Levenshtein
    import Levenshtein
    Levenshtein.distance("fuzzy", "wuzzy")
    # 1

SeatGeek's `fuzzywuzzy <https://github.com/seatgeek/fuzzywuzzy>`__: As described in a `blog post <http://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/>`__, some distance variants that people have found to work well in practice. Its responses are phrased as integer percent similarities; one way to make a distance is to subtract from 100.

.. code:: python

    # pip install fuzzywuzzy
    from fuzzywuzzy import fuzz
    100 - fuzz.ratio("Levensthein", "Leviathan")
    # 50

There are a ton of distances, even just within the two packages mentioned! You can also make your own! (This is encouraged!)
