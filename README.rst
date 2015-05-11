mergic: workflow support for reproducible deduplication and merging
===================================================================

With the ``mergic.Blender``:

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

Distances
---------

Here are some popular distances and how to do them with Python:

-  `Levenshtein string edit
   distance <http://en.wikipedia.org/wiki/Levenshtein_distance>`__: The
   classic! It has many implementations; one of them is
   `python-Levenshtein <http://www.coli.uni-saarland.de/courses/LT1/2011/slides/Python-Levenshtein.html>`__.

.. code:: python

    # pip install python-Levenshtein
    import Levenshtein
    Levenshtein.distance("fuzzy", "wuzzy")
    # 1

-  SeatGeek's `fuzzywuzzy <https://github.com/seatgeek/fuzzywuzzy>`__:
   As described in a `blog
   post <http://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/>`__,
   some distance variants that people have found to work well in
   practice. Its responses are phrased as integer percent similarities;
   one way to make a distance is to subtract from 100.

.. code:: python

    # pip install fuzzywuzzy
    from fuzzywuzzy import fuzz
    100 - fuzz.ratio("Levensthein", "Leviathan")
    # 50

There are a ton of distances, even just within the two packages
mentioned! You can also roll your own! (This is encouraged!)
