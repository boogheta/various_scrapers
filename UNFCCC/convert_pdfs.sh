#!/bin/bash

for file in `ls pdfs/`; do
  res=`pdftotext -eol dos pdfs/$file txts/$file.txt 2>&1`
  if echo $res | grep Error; then
    echo $file
  fi
done > error_convert_pdfs.log

