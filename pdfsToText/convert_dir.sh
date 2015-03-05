#!/bin/bash

dir=$1

mkdir -p txt/$dir

ls $dir | while read f; do
  ./convert_pdf.sh "$dir/$f" "txt/$dir/$f.txt"
done
