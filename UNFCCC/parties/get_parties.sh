#!/bin/bash

mkdir -p html
curl -s "http://unfccc.int/documentation/submissions_from_parties/items/5916.php" > html/COP-CMP
curl -s "http://unfccc.int/documentation/submissions_from_parties/items/5901.php" > html/SBSTA
curl -s "http://unfccc.int/documentation/submissions_from_parties/items/5902.php" > html/SBI
curl -s "http://unfccc.int/kyoto_protocol/items/4752.php" > html/AWG-KP
curl -s "http://unfccc.int/bodies/awg-lca/items/4578.php" > html/AWG-LCA
curl -s "http://unfccc.int/bodies/awg/items/7398.php" > html/ADP

rm -f parties-submissions.csv
for id in `ls html`; do
  cat html/$id | tr '\n' ' ' | sed 's/<\/tr>/\n/g' | sed 's/\&nbsp;/ /g' | sed 's/\&eacute;/é/g' | sed "s/\&\(rsquo\|#39\);/'/g" | sed 's/\$amp;/\&/g' | sed 's/\&oacute/ò/g' | sed 's/;/,/g' | sed 's/\s\+/ /g' | grep "\.pdf" | grep -v 'class="mT"' | grep '<td>' | sed 's#</\?p[^>]*>##g' | sed 's/\s*<tr[^>]*>\s*<td[^>]*>\s*//' | sed 's/\s*<\/td>\s*<td[^>]*>\s*/;/' | sed 's#\s*</td>\s*<td[^>]*>\s*<a href="/\?#;http://unfccc.int/#' | sed 's/"\s*target=\s*"_blank.*\/>\s*/;/' | sed 's/<\/\?\(br\s*\/\|strong\)>//g' | sed 's#</a>.*$##' | sed "s/^/$id;/" >> parties-submissions.csv
done

mkdir -p pdfs
ct=0
awk -F ";" '{print $4}' parties-submissions.csv | while read url; do
  file=$(echo $url | sed 's#/#_#g' | sed 's/:/-/g')
  echo "$ct : $url -> $file"
  wget -nv $url -O pdfs/$file
  ct=$(($ct + 1))
done
