#!/bin/bash

dir1=$(echo "$1" | sed 's#/$##')
dir2=$(echo "$2" | sed 's#/$##')

if test -z "$dir1" || ! test -d "$dir1" || test -z "$dir2" || ! test -d "$dir2" ; then
  echo "USAGE : bash build_results_from_two_corpora.sh <GOOGLE_RESULTS_DIR_1> <GOOGLE_RESULTS_DIR_2>"
  echo "Please input valid paths for <GOOGLE_RESULTS_DIR_1> <GOOGLE_RESULTS_DIR_2>"
  exit 1
fi

rm -f "corpus_results_text_canola-$dir1-$dir2.csv" "corpus_results_text_canola-$dir1-$dir2.csv"
echo '"url","keywords","corpora","format","text"' > "corpus_results_text_raw-$dir1-$dir2.csv"
echo '"url","keywords","corpora","format","text"' > "corpus_results_text_canola-$dir1-$dir2.csv"


cat "$dir1/2-results-urls.csv" "$dir2/2-results-urls.csv" | sort -u | while read url; do
  md5=$(echo "$url" | md5sum | sed 's/\s\+.*$//')
  ext=$(echo "$url" | sed 's/^.*\.\(.\{3,4\}\)$/\1/' | sed 's/^http.*$/html/' | sed 's/[^a-z0-9]//ig')
  corpora=""
  keywords1=$(grep ",\"$url\"," "$dir1/1-results.csv" | sed 's/","http.*$//i' | sed 's/^"//' | tr '\n' '|' | sed 's/|$//')
  if ! test -z "$keywords1"; then
    keywords=$keywords1
    corpora=$dir1
    dir=$dir1
  fi
  keywords2=$(grep ",\"$url\"," "$dir2/1-results.csv" | sed 's/","http.*$//i' | sed 's/^"//' | tr '\n' '|' | sed 's/|$//')
  if ! test -z "$keywords2"; then
    if test -z "$corpora"; then
      keywords=$keywords2
      corpora=$dir2
      dir=$dir2
    else
      corpora="$dir1|$dir2"
      keywords="$keywords1|$keywords2"
    fi
  fi
  textraw=""
  if [ -f "$dir/txt-raw/$md5.txt" ]; then
    textraw=$(cat "$dir/txt-raw/$md5.txt" | tr '\n' ' ' | sed 's/"/""/g' | sed 's/\(\n\|\r\|\t\|\s\)\+/ /g' | sed 's/^\s\+//' | sed 's/\s\+$//')
  fi
  echo "\"$url\",\"$keywords\",\"$corpora\",\"$ext\",\"$textraw\"" >> "corpus_results_text_raw-$dir1-$dir2.csv"
  textcanola=""
  if [ -f "$dir/txt-canola/$md5.txt" ]; then
    textcanola=$(cat "$dir/txt-canola/$md5.txt" | tr '\n' ' ' | sed 's/"/""/g' | sed 's/\(\n\|\r\|\t\|\s\)\+/ /g' | sed 's/^\s\+//' | sed 's/\s\+$//')
  fi
  echo "\"$url\",\"$keywords\",\"$corpora\",\"$ext\",\"$textcanola\"" >> "corpus_results_text_canola-$dir1-$dir2.csv"
done

grep ',""$' "corpus_results_text_canola-$dir1-$dir2.csv" "corpus_results_text_raw-$dir1-$dir2.csv" | sed 's/^[^:]*://' | sort -u > "corpus_results_missing_text-$dir1-$dir2.csv"

