#!/bin/bash

dir=$1
rm -f results.csv
echo "query,url,domain" > results.csv

for file in `ls $dir`; do
  query=""
  cat $dir/$file | while read line; do
    if [ -z "$query" ]; then
      query=$(echo $line | sed 's/^{"query":"//' | sed 's/","lang".*$//' | sed 's/"/""/g')
    else
      url=$(echo $line | sed 's/^.*"url":"//' | sed 's/","summary".*$//' | sed 's/"/""/g')
      domain=$(echo $url | sed 's#^\(https\?://[^/]*/\).*$#\1#')
      echo '"'$query'","'$url'","'$domain'"' >> results.csv
    fi
  done  
done

