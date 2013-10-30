#!/bin/bash
# Si nécessaire récupérer le cookie et les api_sig, api_key, auth_hash et cb depuis la console Chrome en regardant par exemple https://secure.flickr.com/groups/whats_in_your_bag/pool/map?mode=group une fois loggé

GROUP="52241283780@N01"
COOKIE=$(cat cookie.txt)
USERAGENT="Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/28.0.1500.71 Chrome/28.0.1500.71 Safari/537.36"

mkdir -p "$GROUP"
PAGE=1
TOTALPAGES=
while [ -z "$TOTALPAGES" ] || [ "$PAGE" -le "$TOTALPAGES" ] ; do
  curl -X POST --cookie "$COOKIE" -A "$USERAGENT" -d api_sig=4616fc14511487354eccecc8e30c1b9e -d api_key=9ccb5d7a03b222d2a45f8d11a9ab7dcc -d auth_hash=e15df6bca854ec55e6d7d84744c2f071 -d cb=1383154863887 -d accuracy=1 -d extras=owner_name,geo,media -d format=json -d nojsoncallback=1 -d min_taken_date="1970-01-01 00=00=00" -d sort=date-posted-desc -d method=flickr.photos.search -d src=js -d per_page=500 -d "group_id=$GROUP" -d ticket_number=$PAGE -d page=$PAGE "https://secure.flickr.com/services/rest/" > "$GROUP/$PAGE.json"
  PAGE=$(($PAGE + 1))
  if [ -z "$TOTALPAGES" ]; then
    TOTALPAGES=$(cat "$GROUP/$PAGE.json" | sed 's/^.*, "pages"://' | sed 's/, "perpage".*$//')
  fi
done


# Metas user : https://secure.flickr.com/people/photo["owner"]/
# -> slug : link Photostream https://secure.flickr.com/photos/SLUG/
# -> # photos
# -> "Joined:"
# -> "I am:"
# -> groups/following NOT
#
# Photo page : https://secure.flickr.com/photos/photo["owner"]/photo["id"]/
# -> date: https://secure.flickr.com/photos/wombat_juice/archives/date-taken/2013/10/29/
# -> original photo: https://secure.flickr.com/photos/SLUG/ID/sizes/o/ -> link "Download the Original size of this photo"
# -> tags: '<div id="photo-sidebar-tags"'
# -> tags objets: '<span class="note-wrap"'


