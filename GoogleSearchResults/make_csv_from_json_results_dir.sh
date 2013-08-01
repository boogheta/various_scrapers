#!/bin/bash

dir=$(echo "$1" | sed 's#/$##')
rm -f "$dir/1-results.csv"
echo "query,url,domain,is_pdf" > "$dir/1-results.csv"

for file in `ls "$dir/json"`; do
  query=""
  cat "$dir/json/$file" | while read line; do
    if [ -z "$query" ]; then
      query=$(echo "$line" | sed 's/^{"query":"//' | sed 's/","lang".*$//' | sed 's/"/""/g')
    else
      url=$(echo "$line" | sed 's/^.*"url":"//' | sed 's/","summary".*$//' | sed 's/"/""/g' | sed 's#^/interstitial?url=##')
      ext=$(echo "$url" | sed 's/^.*\(....\)/\1/')
      pdf=0
      if [ "$ext" == ".pdf" ]; then
        pdf=1
      fi
      domain=$(echo "$url" | sed 's#^\(https\?://[^/]*/\).*$#\1#')
      echo '"'$query'","'$url'","'$domain'",'$pdf >> "$dir/1-results.csv"
    fi
  done  
done

cat "$dir/1-results.csv" | sed 's/","http[^"]*",[01]*$//' | sed 's/^.*","//' | grep -v 'query,url' | sort -u > "$dir/2-results-urls.csv"

