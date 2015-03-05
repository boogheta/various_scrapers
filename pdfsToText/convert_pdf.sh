#!/bin/bash

pdf=$1
out=$2
root=`echo "$pdf" | sed "s/.pdf$//"`

echo "--------------------"
echo "WORK ON $root"
echo "--------------------"

pdftohtml "$pdf"

cat "${root}s.html" |
 sed 's/&#160;/ /g' |
 sed 's/\s*\r\s*/ /g' |
 perl -MHTML::Entities -ne 'binmode(STDOUT); print decode_entities($_)' |
 sed 's/<[^>]*>//g' |
 sed 's/\s\+/ /g' > "$out"

rm -f "${root}.html" "${root}s.html" "${root}_ind.html" "${root}*.jpg" "${root}*.png"

echo
