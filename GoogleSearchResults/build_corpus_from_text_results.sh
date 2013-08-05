#!/bin/bash

dir=$(echo "$1" | sed 's#/$##')

if test -z "$dir" || ! test -d "$dir" ; then
  echo "USAGE : bash build_corpus_from_text_results.sh <GOOGLE_RESULTS_DIR>"
  echo "Please input a valid path for <GOOGLE_RESULTS_DIR>"
  exit 1
fi

rm -f "$dir/6-corpus_results_text_raw.csv" "$dir/7-corpus_results_text_canola.csv"
echo "url,keywords,format,text" > "$dir/6-corpus_results_text_raw.csv"
echo "url,keywords,format,text" > "$dir/7-corpus_results_text_canola.csv"

cat "$dir/2-results-urls.csv" | while read url; do
  md5=$(echo "$url" | md5sum | sed 's/\s\+.*$//')
  ext=$(echo "$url" | sed 's/^.*\.\(.\{3,4\}\)$/\1/' | sed 's/^http.*$/html/' | sed 's/[^a-z0-9]//ig')
  keywords=$(grep ",\"$url\"," "$dir/1-results.csv" | sed 's/","http.*$//i' | sed 's/^"//' | tr '\n' '|' | sed 's/|$//')
  textraw=""
  if [ -f "$dir/txt-raw/$md5.txt" ]; then
    textraw=$(cat "$dir/txt-raw/$md5.txt" | tr '\n' ' ' | sed 's/"/""/g' | sed 's/\(\n\|\r\|\t\|\s\)\+/ /g' | sed 's/^\s\+//' | sed 's/\s\+$//')
  fi
  echo "\"$url\",\"$keywords\",\"$ext\",\"$textraw\"" >> "$dir/6-corpus_results_text_raw.csv"
  textcanola=""
  if [ -f "$dir/txt-canola/$md5.txt" ]; then
    textcanola=$(cat "$dir/txt-canola/$md5.txt" | tr '\n' ' ' | sed 's/"/""/g' | sed 's/\(\n\|\r\|\t\|\s\)\+/ /g' | sed 's/^\s\+//' | sed 's/\s\+$//')
  fi
  echo "\"$url\",\"$keywords\",\"$ext\",\"$textcanola\"" >> "$dir/7-corpus_results_text_canola.csv"
done

grep ',""$' "$dir/7-corpus_results_text_canola.csv" "$dir/6-corpus_results_text_raw.csv" | sed 's/^[^:]*://' | sort -u > "$dir/8-missing_text.csv"

