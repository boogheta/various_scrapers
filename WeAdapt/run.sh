#!/bin/bash

curl "http://api.weadapt.org/v1/placemarks/list" > placemarks.json
curl "http://api.weadapt.org/v1/organisations/list" > organisations.json
python json_to_sql.py > orgas-places.sql
cat orgas-places.sql | mysql -u root -p weadapt
echo "SELECT t.tag, COUNT(p.id) as count FROM tag t JOIN placemark_tag p ON t.id = p.tag_id GROUP BY t.id ORDER BY count DESC" | mysql -u root -p weadapt > tags_placemarks.csv
echo "SELECT t.tag, COUNT(p.id) as count FROM tag t JOIN organisation_tag p ON t.id = p.tag_id GROUP BY t.id ORDER BY count DESC" | mysql -u root -p weadapt > tags_organisations.csv

./get_countries.sh
python make_networks.py

