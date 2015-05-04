#!/bin/bash

function resolve {
 curl -w "%{url_effective}" -LsS --insecure --max-redirs 10 -o /dev/null "$1"
}

infile="$1"

cp -f "$infile"{,.tmp}

cat "$infile" |
 sed -r 's/(https?:)/\n\1/g' |
 sed -r 's/( |",)/\n/g' |
 sed 's/[…"”\.)]\+$//' |
 sed 's/#[^\/#]*$//' |
 grep "https\?://......" |
 sort -ru |
 grep -v "twitter.com/" |
 while read url; do
  good=$(resolve $url)
  if ! [ "$url" = "$good" ]; then
   echo "$url  --> $good"
   cat "$infile".tmp |
    replace "$url" "$good " > "$infile".tmp2
   mv -f "$infile".tmp{2,}
  fi
 done

echo "Resolved urls applied in $infile.tmp"
