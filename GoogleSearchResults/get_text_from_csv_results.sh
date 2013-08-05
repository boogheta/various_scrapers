#!/bin/bash

dir=$(echo "$1" | sed 's#/$##')

if test -z "$dir" || ! test -d "$dir" ; then
  echo "USAGE : bash get_text_from_csv_results.sh <GOOGLE_RESULTS_DIR>"
  echo "Please input a valid path for <GOOGLE_RESULTS_DIR>"
  exit 1
fi

rm -rf "$dir/html-pdf" "$dir/txt" "$dir/txt-canola" "$dir/txt-raw" "$dir/3-results-urls-md5.csv" "$dir/4-download-errors.log" "$dir/5-extraction-errors.log"
echo "url,format,md5" > "$dir/3-results-urls-md5.csv"

cat "$dir/2-results-urls.csv" | while read url; do
  md5=$(echo "$url" | md5sum | sed 's/\s\+.*$//')
  ext=$(echo "$url" | sed 's/^.*\.\(.\{3,4\}\)$/\1/' | sed 's/^http.*$/html/' | sed 's/[^a-z0-9]//ig')
  echo "$url;$ext;$md5" >> "$dir/3-results-urls-md5.csv"
  echo `date`": $url -> $md5 / $ext"
  while [ $(pgrep -fc "python ghost_download.py") -gt 20 ]; do
    ps -e -o time,pid,command | grep ghost_download | sort -r | while read line; do
      proctime=$(echo $line | sed 's/^\(..\):\(..\).*$/\1\2/')
      if [ "$proctime" -gt 45 ]; then
        process=$(echo $line | awk -F " " '{print $2}')
        kill $process
      fi
    done
    sleep 1
  done
  bash "dl_and_extract_text_from_url.sh" "$url" "$dir" &
  sleep 0.5
done

