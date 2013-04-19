#!/bin/bash

echo "placemark_id,country" > placemarks_coords.csv
echo "select id, latitude, longitude from placemark" |
    mysql -u root -p weadapt |
    sed 's/\t/,/g' |
    grep -v latitude |
    while read line; do
        id=`echo "$line" | awk -F ',' '{print $1}'`;
        coords=`echo "$line" | sed 's/^'"$id"',//' | sed 's/,/\&lon=/' | sed 's/\([0-9].[0-9][0-9]\)[0-9]*/\1/g'`;
        country=`curl "http://nominatim.openstreetmap.org/reverse?format=xml&accept-language=en&email=benjamin.oogheATsciences-po.fr&lat=$coords" -s | grep country | sed 's/^.*<country>\(.*\)<\/country>.*$/\1/'`;
        echo "$id,$country";
    done >> placemarks_coords.csv

