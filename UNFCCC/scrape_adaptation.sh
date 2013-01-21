#!/bin/bash

mkdir -p tmp
mkdir -p pdfs
echo "url|id|symbol|title|authors|en_pdf_url|abstract|meeting|doctype|topics|keywords|countries|pubdate" > unfccc_adaptation_metadatas.csv

baseurl="http://unfccc.int/documentation/documents/advanced_search/items/"
searchpage="3594.php?searchterm="
detailspage="6911.php?priref="
lastyear=2005
for search in "adaptation" "vulnerability" "climate+impact"; do
  maxpage=`curl "$baseurl$searchpage$search" -s -S | grep "go to last page" | sed 's/^.*&page=//' | sed 's/" title=.*$//'`
  for i in `seq $maxpage`; do
    url="$baseurl$searchpage$search&page=$i"
    echo "Process page $i for keyword $search : $url"
    #curl "$url" --connect-timeout 30 --retry 5 -s -S > tmp/recherche-$search-$i.html
    if [ `grep -vc "6911.php?priref=" tmp/recherche-$search-$i.html` -eq 0 ]; then
      curl "$url" --connect-timeout 30 --retry 5 -s -S > tmp/recherche-$search-$i.html
    fi
    grep "6911.php?priref=" tmp/recherche-$search-$i.html | sed 's/6911.php?priref=/\n/g' | grep "<img " | sed 's/"><img.*&nbsp;\([O\-9]\{4\}\)<\/td>.*$/;\1/' > tmp/recherche-$search-$i.ids
    for u in `cat tmp/recherche-$search-$i.ids`; do
      annee=`echo $u | awk -F ";" '{print $2}'`
      if [ $annee -ge $lastyear ]; then
        continue;
      fi
      id=`echo $u | awk -F ";" '{print $1}'`
      url="$baseurl$detailspage$id"
      if ! test -e tmp/dataset-$id.html; then
        curl "$url" --connect-timeout 30 --retry 5 -s -S > tmp/dataset-$id.html
      fi
      if [ `grep -vc "adlibsearch_label_container_left" tmp/dataset-$id.html` -eq 0 ]; then
        curl "$url" --connect-timeout 30 --retry 5 -s -S > tmp/dataset-$id.html
      fi
      ct=0
      fields="$url"
      grep '"adlibsearch_text_container_right' tmp/dataset-$id.html | sed 's#\s*<\/\?div[^>]*>\s*##g' | while read line; do
        case "$ct" in
          0) id=`echo $line | sed 's#/#_#g'`
             fields="$fields|$id|$line";;
          3) pdfurl=`echo $line | sed 's#^.* href="\([^"]\+\)"[^>]*>\s*<img[^>]*>\s*EN.*$#\1#'`
             if [ "$pdfurl" == "$line" ]; then
               pdfurl=""
             else
               wget "$pdfurl" -O pdfs/$id.pdf
             fi
             fields="$fields|$pdfurl";;
          4) ;;
          6) ;;
         12) date=`echo $line | sed 's#^.* \([0-9]\+\)/\([0-9]\+\)/\([0-9]\{4\}\).*$#\3-\2-\1#'`
             echo "$fields|$date" >> unfccc_adaptation_metadatas.csv;;
          *) line=`echo $line | sed 's#\(\s*<[^>]*>\s*\)\+#,#g' | sed 's/^-$//' | sed 's/,$//' | sed 's/^,//'`
             fields="$fields|$line";;
        esac
        ct=$(($ct + 1))
      done
    done
  done
done

