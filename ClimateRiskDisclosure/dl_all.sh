#!/bin/bash

mkdir -p data

echo "[" > all_data.json
cat Oil_Gas_Russell_3000_2009-2014.csv  |
  grep -v "^coname,"                    |
  sed 's/^.*,\([^,]*\)\r$/\1/'          |
  while read fid; do
    if ! test -s "data/$fid.json"; then
      echo "downloading $fid"
      curl -sL "http://www.climateriskdisclosure.org/api/climatedisclosure_medialab.php?filename=$fid" > "data/$fid.json"
    fi
    cat "data/$fid.json" | sed 's/$/,/'
  done | sed 's/,$//' >> all_data.json
echo "]" >> all_data.json
