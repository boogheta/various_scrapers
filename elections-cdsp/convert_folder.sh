#!/bin/bash

folder=$1

header="^\(numéro\|code\)"

for file in `ls $folder/*.xls*`; do
  rootfile=${file%.xlsx}
  rootfile=${rootfile%.xls}
  echo $rootfile
  unoconv -f csv --stdout "$file" | iconv -f "latin1" -t "utf8" > "$rootfile.tmp"
  grep -A `cat $rootfile.tmp | wc -l` -i "$header" "$rootfile.tmp" > "$rootfile.csv"
  grep -B 100 -i "$header" "$rootfile.tmp" | grep -v -i "$header" | tr '\n' ' ' | sed 's/"\?,,\+"\?/\n/g' | grep . > "$rootfile.txt"
  rm -f "$rootfile.tmp"
  echo "  ->  "`cat "$rootfile.csv" | wc -l`
done

cur=""
ls $folder/*comm*00*.csv 2> /dev/null | while read comfile; do
  ser=`echo $comfile | sed 's/^\(.*\_comm\).*$/\1/'`
  if [ "$cur" = $ser ]; then
    cur=""
    echo "Assembling communes files for $ser"
    suf=""
    if ! (ls $ser*3500.csv > /dev/null 2>&1 || ls $ser*3500-ag.csv > /dev/null 2>&1 ); then
     suf="p3500"
    fi
    head -1 $ser*.csv | grep "," | grep -v "==>" | uniq > $ser$suf.tmp
    cat $ser*00*.csv | grep -i -v "$header" | sort -t "," -k 1n -k 3n >> $ser$suf.tmp
    mkdir -p old
    mv $ser*00*.csv old/
    mv $ser$suf.{tmp,csv}
    cat $ser*00*.txt > $ser$suf.txt.tmp
    mv $ser*00*.txt old/
    mv $ser$suf.txt{.tmp,}
  else
    cur=$ser
  fi
done

mkdir -p $folder/xls $folder/csv
mv $folder/*.xls* $folder/xls/
zip -r $folder/$folder-xls.zip $folder/xls
mv $folder/*.csv $folder/csv/
mv $folder/*.txt $folder/csv/
zip -r $folder/$folder-csv $folder/csv
