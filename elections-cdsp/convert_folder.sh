#!/bin/bash

header="^\(numéro\|code\)"

for file in `ls $1/*.xls`; do
  rootfile=${file%.xls}
  echo $rootfile
  unoconv -f csv --stdout "$file" | iconv -f "latin1" -t "utf8" > "$rootfile.tmp"
  grep -A `cat $rootfile.tmp | wc -l` -i "$header" "$rootfile.tmp" > "$rootfile.csv"
  grep -B 100 -i "$header" "$rootfile.tmp" | grep -v -i "$header" | tr '\n' ' ' | sed 's/"\?,,\+"\?/\n/g' | grep . > "$rootfile.txt"
  rm -f "$rootfile.tmp"
  echo "  ->  "`cat "$rootfile.csv" | wc -l`
done
