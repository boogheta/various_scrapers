#!/bin/bash

dir=$(echo "$1" | sed 's#/$##')
    rm -rf "$dir/html-pdf" "$dir/txt-canola" "$dir/txt-num" "$dir/3-results-urls-md5.csv" "$dir/4-download-errors.log" "$dir/5-extraction-errors.log"
    mkdir -p "$dir/html-pdf" "$dir/txt"
echo "url,md5" > "$dir/3-results-urls-md5.csv"

cat "$dir/2-results-urls.csv" | while read url; do
  md5=$(echo $url | md5sum | sed 's/\s\+.*$//')
  ext=$(echo "$url" | sed 's/^.*\(....\)/\1/')
  if [ "$ext" == ".pdf" ]; then
    ext="pdf"
  else
    ext="html"
  fi
  echo `date`": $url;$ext;$md5" >> "$dir/3-results-urls-md5.csv"
  echo "$url -> html/$md5.$ext - txt/$md5.txt"
  while [ $(pgrep -fc dl_and_extract_text_from_url.sh) -gt 10 ]; do
    sleep 1
  done
  bash "dl_and_extract_text_from_url.sh" "$url" "$dir" "$md5" "$ext" &
  sleep 0.5
done
