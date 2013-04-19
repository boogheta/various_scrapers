#!/bin/bash

cd `echo $0 | sed 's/[^\/]*$//'`

url="http://tel.sciences-po.fr/export/exportcsv/valrecherche/"
endurl="/tri/NOM/typetri/ASC"
output="annuaire.csv"
letters="a b c d e f g h i j k l m n o p q r s t u v w x y z"
touch $output
total=`wc -l $output | awk '{print $1}'`

date
for a in $letters; do
  for b in $letters; do
    for c in $letters; do
      oldtotal=$total
      curl "$url$a$b$c$endurl" | grep -v '   ;' >> annuaire.csv 2> /dev/null
      sort annuaire.csv | uniq > annuaire.csv.tmp
      mv annuaire.csv.tmp annuaire.csv
      total=`wc -l $output | awk '{print $1}'`
      echo "$a$b$c / $total noms in $output"
    done
  done
done
date

