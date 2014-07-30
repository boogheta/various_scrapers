#!/bin/bash

labelsfile="$1"
gexffile="$2"

if ! test -f "$labelsfile" || ! test -f "$gexffile" ||
 ! echo "$labelsfile" | grep "\.csv$"  > /dev/null  ||
 ! echo "$gexffile"   | grep "\.gexf$" > /dev/null  ||
 ! head -n 1 "$labelsfile" | grep -i "^id,label" > /dev/null; then
  echo "ERROR: one of the inputs is not a valid file"
  echo "SYNTAX: bash set_labels_as_ids.sh labels_file.csv gexf_file.gexf"
  echo "labels_file.csv should be formatted as follows:"
  echo "id,label"
  echo "ID1,LABEL1"
  echo "ID2,LABEL2"
  echo "..."
  echo "this is intended to work with ids generated from table2net"
  echo "ids should not contain any other special character than _"
  echo "unicity of labels is not checked for, please make sure they are beforehand"
  exit 1
fi

cp "$gexffile"{,.tmp}
cat "$labelsfile" | while read line; do
  id=$(echo $line | awk -F ',' '{print $1}' | sed 's#/#\\/#g')
  label=$(echo $line | awk -F ',' '{print $2}' | sed 's#/#\\/#g' | sed 's/[\r\n]\+//g' | sed 's/""/\\\&quot;/g' | sed 's/^"//' | sed 's/"$//')
  sed 's/ \(id\|source\|target\)="'"$id"'"/ \1="'"$label"'"/g' "$gexffile".tmp > "$gexffile".tmp2
  mv "$gexffile".tmp{2,}
done

mv "$gexffile".tmp $(echo "$gexffile" | sed 's/.gexf/_newids.gexf/')

