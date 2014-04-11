#!/bin/bash

source $(which virtualenvwrapper.sh)
workon test

if [ -z $1 ]; then
  echo "Downloading source json from WeAdapt's API..."
  curl "http://api.weadapt.org/v1/placemarks/list" > placemarks.json
  curl "http://api.weadapt.org/v1/organisations/list" > organisations.json
fi
echo "Converting to sql..."
python json_to_sql.py > orgas-places.sql
echo "Saving to local MySQL..."
cat orgas-places.sql | mysql -u root -p weadapt
echo "Querying placemark_tags from local MySQL..."
echo "SELECT t.tag, COUNT(p.id) as count FROM tag t JOIN placemark_tag p ON t.id = p.tag_id GROUP BY t.id ORDER BY count DESC" | mysql -u root -p weadapt > tags_placemarks.csv
echo "Querying placemark_tags from local MySQL..."
echo "SELECT t.tag, COUNT(p.id) as count FROM tag t JOIN organisation_tag p ON t.id = p.tag_id GROUP BY t.id ORDER BY count DESC" | mysql -u root -p weadapt > tags_organisations.csv
echo "Collecting placemarks from MySQL and associate with country names via nominatim..."
./get_countries.sh
echo "Building GEXF network files..."
python make_networks.py
echo "All done!"
echo

