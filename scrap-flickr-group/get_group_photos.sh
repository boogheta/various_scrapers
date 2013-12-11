#!/bin/bash


GROUP=$1
if [ -z "$GROUP" ]; then
  echo "Please provide a group name to scrap"
  echo
  exit 1
fi

mkdir -p "data/$GROUP"

PAGE=1
REALPAGE=1
LASTGOOD=0
TOTALPAGES=
MAXDATE=$(date +"%Y-%m-%d 23:59:59")

source flickrcall.sh
while [ -z "$TOTALPAGES" ] || [ "$REALPAGE" -le "$TOTALPAGES" ] ; do
  if ! [ -f "data/$GROUP0/$REALPAGE.json" ] || ! grep '"photo":\[{' "data/$GROUP0/$REALPAGE.json" > /dev/null; then
    echo " - Downloading 350-results page #$REALPAGE (out of $TOTALPAGES) for « $GROUP0 » (page $PAGE with max date $MAXDATE)..."
    ct=0
    retry=true
    while $retry && [ $ct -lt 3 ]; do
      sleep 0.1
      $callflickr -d method=flickr.photos.search -d "group_id=$GROUP" -d per_page=350 -d page=$PAGE -d extras=owner_name,geo,media,description,license,date_upload,date_taken,icon_server,original_format,last_update,tags,machine_tags,o_dims,views,path_alias,url_q,url_t,url_s,url_z,url_o -d sort="date-posted-desc" -d min_taken_date="1970-01-01 00:00:00" -d max_taken_date="$MAXDATE" > "data/$GROUP0/$REALPAGE.json"
      if [ $? -eq 0 ]; then
        retry=false
      fi
      ct=$(($ct + 1))
    done
    if $retry; then
      echo "    !!WARNING GOT NO RESULT ON CURL QUERY!!"
      exit 1
    fi
  else
    echo " - Skipping download of page #$REALPAGE (out of $REALT) for « $GROUP0 » already in cache..."
  fi
  if [ -z "$TOTALPAGES" ]; then
    TOTALPAGES=$(cat "data/$GROUP0/1.json" | sed 's/^.*, "pages"://' | sed 's/, "perpage".*$//')
  fi
  LAST=$(($REALPAGE - 1))
  if [ "$LAST" -gt 0 ] && ! grep '"photo":\[{' "data/$GROUP0/$REALPAGE.json" > /dev/null && grep '"datetaken":' "data/$GROUP0/$LAST.json" > /dev/null; then
    LASTGOOD=$LAST
    MAXDATE=$(cat "data/$GROUP0/$LAST.json" | sed 's/^.*"dateupload":"\([^"]\+\)"[^{]*$/\1/')
    PAGE=1
    LEFT=$(($TOTALPAGES - $LAST))
    echo "    WARNING: reached max results for query, adjusting min upload date to $MAXDATE, $LEFT left to do"
  else
    PAGE=$(($PAGE + 1))
  fi
  REALPAGE=$(($PAGE + $LASTGOOD))
done

echo " All done!"
echo


