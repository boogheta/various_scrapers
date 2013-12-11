#!/bin/bash

GROUP=$1
if [ -z "$GROUP" ]; then
  echo "Please provide a group name to scrap"
  echo
  exit 1
fi

mkdir -p "data/$GROUP"

if ! test -f "data/$GROUP/metas.json"; then
  source flickrcall.sh
  $callflickr -d method=flickr.groups.getInfo -d "group_id=$GROUP" > "data/$GROUP/metas.json"
fi

