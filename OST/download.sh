#!/bin/bash

url=$1
if test -z "$url"; then
  url="http://downloads.khinsider.com/game-soundtracks/album/little-big-adventure-2-twinsen-s-odyssey-original-soundtrack"
fi

dir=$(echo $url | sed 's|^.*/\([^/]\+\)/\?$|musique/\1|')
mkdir -p "$dir"

curl -sL "$url"      |
 grep "href=.*\.mp3" |
 sed 's/^.*href="//' |
 sed 's/".*$//'      |
 sort -u             |
 while read url; do
  fileurl=$(curl -sL "$url" |
   grep "href=.*\.mp3"      |
   sed 's/^.*href="//'      |
   sed 's/".*$//'           |
   head -n 1)
  filename=$(echo $fileurl  |
   sed 's|^.*/\([^/]\+\)$|\1|')
  echo $dir/$filename
  if ! test -s "$dir/$filename"; then
    wget -q "$fileurl" -O "$dir/$filename"
    echo "...downloaded"
    echo
  fi
done
