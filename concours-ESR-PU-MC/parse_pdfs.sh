#!/bin/bash

mkdir -p data pdfmaps

for pdffile in pdfs/*.pdf; do
  echo "WORKING ON $pdffile ..."
  pdftohtml -xml "$pdffile" > /dev/null
  xmlfile=$(echo $pdffile | sed 's/\.pdf$/.xml/')
  # draw maps
  ./parse_xml_from_pdfs.py "$xmlfile" 1
  csvfile=$(echo $pdffile | sed 's/\.pdf$/.csv/' | sed 's#pdfs/#data/#')
  ./parse_xml_from_pdfs.py "$xmlfile" > "$csvfile"
done

