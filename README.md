# uno

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

```bash
# How many unique players?
tail +2 names_merge.txt | cut -d, -f2 | sort | uniq | wc -l
# 359
```
