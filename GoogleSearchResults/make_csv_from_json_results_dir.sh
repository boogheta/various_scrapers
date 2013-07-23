#!/bin/bash

dir=$1
rm -f $dir/1-results-$dir.csv
echo "query,url,domain,is_pdf" > $dir/1-results-$dir.csv

for file in `ls $dir/json`; do
  query=""
  cat $dir/json/$file | while read line; do
    if [ -z "$query" ]; then
      query=$(echo $line | sed 's/^{"query":"//' | sed 's/","lang".*$//' | sed 's/"/""/g')
    else
      url=$(echo $line | sed 's/^.*"url":"//' | sed 's/","summary".*$//' | sed 's/"/""/g')
      ext=$(echo $url | sed 's/^.*\(....\)/\1/')
      pdf=0
      if [ "$ext" == ".pdf" ]; then
        pdf=1
      fi
      domain=$(echo $url | sed 's#^\(https\?://[^/]*/\).*$#\1#')
      echo '"'$query'","'$url'","'$domain'",'$pdf >> $dir/1-results-$dir.csv
    fi
  done  
done

