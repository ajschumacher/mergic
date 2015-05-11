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
