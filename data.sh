#!/usr/bin/env bash

wget https://archive.ics.uci.edu/ml/machine-learning-databases/00300/Tennis-Major-Tournaments-Match-Statistics.zip

unzip Tennis-Major-Tournaments-Match-Statistics.zip

if [ -a names_all.txt ]
then
    rm names_all.txt
fi

for filename in *.csv
do
    for field in 1 2
    do
        tail +2 $filename | cut -d, -f$field >> names_all.txt
    done
done

echo currently $(sort names_all.txt | uniq | wc -l) unique names in names_all.txt
