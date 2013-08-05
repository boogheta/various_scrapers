#!/bin/bash

url="$1"
dir=$(echo "$2" | sed 's#/$##')

md5=$(echo "$url" | md5sum | sed 's/\s\+.*$//')
ext=$(echo "$url" | sed 's/^.*\.\(.\{3,4\}\)$/\1/' | sed 's/^http.*$/html/' | sed 's/[^a-z0-9]//ig')

mkdir -p "$dir/html-pdf" "$dir/txt" "$dir/txt-canola" "$dir/txt-raw"
touch "$dir/html-pdf/$md5.$ext" "$dir/txt-raw/$md5.txt" "$dir/txt-canola/$md5.txt"

contenttype=$(curl --connect-timeout 5 -sLI "$url" 2> /dev/null | grep -i "^Content-Type:" | sed 's/^.*Type:\s*//' | sed 's/^.*application.*pdf.*$/pdf/' | sed 's/^.*application.*$/application/')

if [ "$ext" == "pdf" ] || [ "$contenttype" == "pdf" ] ; then
  ct=0
  while [ $(stat -c%s "$dir/html-pdf/$md5.$ext") -eq 0 ]; do
    ct=$(( $ct + 1 ))
    if [ $ct -gt 10 ]; then
      echo "ERROR DL: Skipping $url after 10 missed tryouts" >> "$dir/4-download-errors.log"
      exit 1
    fi
    wget "$url" --dns-timeout 30 --connect-timeout 60 --read-timeout 300 -q -O "$dir/html-pdf/$md5.$ext" 2>> "$dir/4-download-errors.log"
  done
  pdftotext -nopgbrk "$dir/html-pdf/$md5.$ext" "$dir/PDF$md5.tmp" 2>> "$dir/5-extraction-errors.log" 2>> "$dir/5-extraction-errors.log"
  if [ "$?" -eq 0 ]; then
    cat "$dir/PDF$md5.tmp" | tr '\n' ' ' | sed 's/\(\n\|\r\|\t\|\s\)\+/ /g' > "$dir/txt-raw/$md5.txt"
    cp "$dir/txt-raw/$md5.txt" "$dir/txt-canola/$md5.txt"
    rm -f "$dir/PDF$md5.tmp"
  fi
elif [ "$contenttype" != "application" ]; then
  source /usr/local/bin/virtualenvwrapper.sh
  workon boilerpy
  python ghost_download.py "$url" "$dir/html-pdf/$md5.$ext" >> "$dir/4-download-errors.log" 2>&1
  python extractTxtFromHtml_BoilerPipe.py "$dir/html-pdf/$md5.$ext" "RegExp" > "$dir/txt-raw/$md5.txt"  2>> "$dir/5-extraction-errors.log"
  python extractTxtFromHtml_BoilerPipe.py "$dir/html-pdf/$md5.$ext" "CanolaExtractor" > "$dir/txt-canola/$md5.txt"  2>> "$dir/5-extraction-errors.log"
  deactivate
fi



#  python extractTxtFromHtml_BoilerPy.py "$dir/html-pdf/$md5.$ext" "CANOLA_EXTRACTOR" > "$dir/txt-canola/$md5.txt" 2>> "$dir/5-extraction-errors.log"
#  python extractTxtFromHtml_BoilerPy.py "$dir/html-pdf/$md5.$ext" "NUM_WORDS_RULES_EXTRACTOR" > "$dir/txt-num/$md5.txt" 2>> "$dir/5-extraction-errors.log"
#  python extractTxtFromHtml_BoilerPipe.py "$dir/html-pdf/$md5.$ext" "CanolaExtractor" > "$dir/txt-canola/$md5.txt" 2>> "$dir/5-extraction-errors.log"
#  python extractTxtFromHtml_BoilerPipe.py "$dir/html-pdf/$md5.$ext" "NumWordsRulesExtractor" > "$dir/txt-num/$md5.txt" 2>> "$dir/5-extraction-errors.log"

#  python dlAndExtractText.py "$url" "CanolaExtractor" > "/tmp/$md5.txt" 2>> "$dir/5-extraction-errors.log"
#  grep -v "^#" "/tmp/$md5.txt" > "$dir/txt-canola/$md5.txt"
#  python dlAndExtractText.py "$url" "KeepEverythingExtractor" > "/tmp/$md5.txt" 2>> "$dir/5-extraction-errors.log"
#  grep -v "^#" "/tmp/$md5.txt" > "$dir/txt-num/$md5.txt"

#  python extractTxtFromHtml_BoilerPipe.py "$dir/html-pdf/$md5.$ext" "KeepEverythingExtractor" > "$dir/txt-num/$md5.txt"  2>> "$dir/5-extraction-errors.log"

