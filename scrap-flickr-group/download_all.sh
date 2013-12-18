#!/bin/bash

# USAGE ./download_all.sh # 
# or ./download_all.sh 1  # To skip dl-check/update of groups data
# If necessary get api_key from Chrome's console by checking args fo the REST query from <https://secure.flickr.com/groups/whats_in_your_bag/pool/map?mode=group> for instance, ideally after having logged if with an account subscribing to the group
# Set APIKEY in flickrcall.sh accordingly

source flickrcall.sh

if [ -z $1 ]; then

# Download metas on group and metas on all photos from the group via FlickR's API
  for GROUPNAME in $(cat list_groups.txt); do
    echo "WORKING ON GROUP $GROUPNAME"
    # Get real group ID from name if name given instead of id
    if ! echo "$GROUPNAME" | grep "@"; then
      echo " - Getting real group id for « $GROUPNAME »..."
      GROUP=$(curl -sL "https://secure.flickr.com/groups/$GROUPNAME/" |
        grep "/groups_join.gne?id=.*@" |
        head -n 1 |
        sed 's/^.*gne?id=//' |
        sed 's/".*$//')
      if ! echo "$GROUP" | grep "@"; then
        echo "   ...failed : $GROUP" 
        echo
        exit 1
      fi 
    else
      GROUP=$GROUPNAME
    fi
    mkdir -p "data/$GROUP"
    ./get_group_metas.sh $GROUP
    ./get_group_photos.sh $GROUP
  done

  # Save the data in mongo
  for id in $(ls data); do
    for file in $(ls data/$id | grep json); do
      echo "$id/$file";
      python save_in_mongo.py data/$id/$file $id
    done
  done

fi

# Collect metas on all authors of the photos:
# Export the ids of all different authors of the photos
mkdir -p data/users
mongoexport --db flickr --collection photos --csv -f "owner" | sort -u | sed 's/"//g' | grep -v '^owner' > list_users.csv
for user in $(cat list_users.csv); do
  if test -s "data/users/$user.json" && grep "username" "data/users/$user.json" > /dev/null; then
    continue
  fi
  ct=0
  retry=true
  while $retry && [ $ct -lt 3 ] ; do
    sleep 1
    echo "get user $user"
    $callflickr -d method=flickr.people.getInfo -d user_id="$user" > "data/users/$user.json"
    if [ $? -eq 0 ]; then
      retry=false
    fi
    ct=$(($ct + 1))
  done
  if $retry ; then
    echo "    !!WARNING GOT NO RESULT ON QUERY for user $user !!" >> errors.txt
  fi
done

#Save in mongo:
for user in $(cat list_users.csv); do
  python save_in_mongo.py data/users/$user.json
done

# Scrap from FlickR's webpages special object tags missing from API
# Export the ids of all photos
mongoexport --db flickr --collection photos --csv -f "_id" | sed 's/"//g' | grep -v '^_id' > list_photos.csv
mkdir -p data/photos
# Download the webpages for every photo
for id in $(cat list_photos.csv); do
  ct=0
  cleanid=$(echo $id | sed 's/\W/-/g')
  if test -s "data/photos/$cleanid.html"; then
    continue
  fi
  retry=true
  while $retry && [ $ct -lt 3 ] ; do
    sleep 1
    curl -sL "https://secure.flickr.com/photos/$id/" > "data/photos/$cleanid.html"
    if [ $? -eq 0 ]; then
      retry=false
    fi
    ct=$(($ct + 1))
  done
  if $retry ; then
    echo "    !!WARNING GOT NO RESULT ON CURL QUERY for photo https://secure.flickr.com/photos/$id/ !!" >> errors.txt
  fi
done

# Extract note-wrap tags from the webpages and add to photo's metas in mongo
for id in $(cat list_photos.csv); do 
  cleanid=$(echo $id | sed 's/\W/-/g')
  cat "data/photos/$cleanid.html" |
    tr '\n' ' ' |
    sed 's/\(<\/\?u\?li\?\)/\n\1/g' |
    grep '<span class="note-wrap' |
    sed 's/^.*style="left://' |
    sed 's/px;\s*\(top\|width\|height\):/,/g' |
    sed 's/px;"><span.*note-wrap">/,/' |
    sed 's/<\/span>.*$//' > temp_tags.txt
  #cat "data/photos/$cleanid.html" | tr '\n' ' ' | sed 's/\(<\/\?span\)/\n\1/g' | grep '<span class="note-wrap' | sed 's/<[^>]\+>//g' > temp_tags.txt
  if grep "." temp_tags.txt > /dev/null; then
    python add_extra_tags.py "$id" temp_tags.txt
  fi
done



