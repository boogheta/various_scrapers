#!/bin/bash

source config.sh

query=$1

rooturl="https://www.googleapis.com/books/v1/volumes?q=$query&maxResults=40&key=$GOOGLE_API_KEY"

mkdir -p data

function download_page {
  lastindex=$(($1 * 40))
  if [ ! -f "data/$query.$1.json" ]; then
    curl -s "$rooturl&startIndex=$lastindex" > "data/$query.$1.json"
  fi
  cat "data/$query.$1.json"
}

totalRes=$(download_page 0 | grep "totalItems" | sed 's/[^0-9]//g')
maxPage=$(($totalRes / 40 - 1))

for i in $(seq $maxPage); do
  download_page $i > /dev/null
done

