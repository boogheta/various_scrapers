#!/bin/bash

url="$1"
dir=$(echo "$2" | sed 's#/$##')
md5="$3"
ext="$4"

if [ -z "$md5" ]; then
  md5=$(echo $url | md5sum | sed 's/\s\+.*$//')
fi
if [ -z "$ext" ]; then
  ext=$(echo "$url" | sed 's/^.*\(....\)/\1/')
  if [ "$ext" == ".pdf" ]; then
    ext="pdf"
  else
    ext="html"
  fi
fi

mkdir -p "$dir/html-pdf" "$dir/txt" "$dir/txt-canola" "$dir/txt-num" "$dir/txt-raw"

ct=0
if [ "$ext" == "pdf" ]; then
  touch "$dir/html-pdf/$md5.$ext"
  while [ $(stat -c%s "$dir/html-pdf/$md5.$ext") -eq 0 ]; do
    ct=$(( $ct + 1 ))
    if [ $ct -gt 10 ]; then
      if [ "$ext" != "pdf" ]; then
        curl -sL "$url" > "$dir/html-pdf/$md5.$ext"
      fi
      if [ $(stat -c%s "$dir/html-pdf/$md5.$ext") -eq 0 ]; then
        echo "ERROR DL: Skipping $url after 10 missed tryouts" >> "$dir/4-download-errors.log"
        exit 1
      else
        break
      fi
    fi
    wget "$url" --dns-timeout 30 --connect-timeout 60 --read-timeout 300 -q -O "$dir/html-pdf/$md5.$ext"
  done
  pdftotext -nopgbrk "$dir/html-pdf/$md5.$ext" "$dir/txt-raw/$md5.txt" 2>> "$dir/5-extraction-errors.log"
  cp "$dir/txt-raw/$md5.txt" "$dir/txt-canola/$md5.txt"
  cp "$dir/txt-raw/$md5.txt" "$dir/txt-num/$md5.txt"
else
  touch "$dir/html-pdf/$md5.$ext" "$dir/txt-canola/$md5.txt" "$dir/txt-num/$md5.txt" "$dir/txt-raw/$md5.txt"
  source /usr/local/bin/virtualenvwrapper.sh
  workon boilerpy
  python ghost_download.py "$url" "$dir/html-pdf/$md5.$ext" >> "$dir/4-download-errors.log" 2>&1
  python extractTxtFromHtml_BoilerPipe.py "$dir/html-pdf/$md5.$ext" "RegExp" > "$dir/txt-raw/$md5.txt"  2>> "$dir/5-extraction-errors.log"
  python extractTxtFromHtml_BoilerPipe.py "$dir/html-pdf/$md5.$ext" "CanolaExtractor" > "$dir/txt-canola/$md5.txt"  2>> "$dir/5-extraction-errors.log"
  python extractTxtFromHtml_BoilerPipe.py "$dir/html-pdf/$md5.$ext" "KeepEverythingExtractor" > "$dir/txt-num/$md5.txt"  2>> "$dir/5-extraction-errors.log"
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

