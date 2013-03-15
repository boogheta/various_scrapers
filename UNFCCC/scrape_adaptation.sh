#!/bin/bash

#keywords="adaptation vulnerability climate+impact adaptative vulnerable"
keywords="a"
baseurl="http://unfccc.int/documentation/documents/advanced_search/items/"
searchpage="3594.php?searchterm="
detailspage="6911.php?priref="
fields="url|pdf_filename|symbol|title|authors|pdf_url|pdf_language|abstract|meeting|doctype|topics|keywords|countries|pubdate|year"
csvfile="unfccc_adaptation_metadatas.csv"
statsfields="year pdf_language doctype countries meeting authors topics keywords"
statsfile="unfccc_adaptation_metadatas.stats"

mkdir -p tmp pdfs
echo "$fields" > $csvfile

for search in $keywords; do
  maxpage=`curl "$baseurl$searchpage$search " -s -S | grep "go to last page" | sed 's/^.*&page=//' | sed 's/" title=.*$//'`
  if [ "$maxpage" == "" ]; then
    maxpage=1
  fi
  for i in `seq $maxpage`; do
    url="$baseurl$searchpage$search&page=$i"
    echo "Process page $i for keyword $search : $url"
    if ! [ -f "tmp/recherche-$search-$i.html" ]; then
      curl "$url" --connect-timeout 30 --retry 5 -s -S > "tmp/recherche-$search-$i.html"
    fi
    if [ `grep -vc "6911.php?priref=" "tmp/recherche-$search-$i.html"` -eq 0 ]; then
      curl "$url" --connect-timeout 30 --retry 5 -s -S > "tmp/recherche-$search-$i.html"
    fi
    grep "6911.php?priref=" "tmp/recherche-$search-$i.html" | sed 's/6911.php?priref=/\n/g' | grep "<img " | sed 's/"><img.*&nbsp;\([O\-9]\{4\}\)<\/td>.*$/;\1/' > "tmp/recherche-$search-$i.ids"
    for u in `cat "tmp/recherche-$search-$i.ids"`; do
      annee=`echo $u | awk -F ";" '{print $2}'`
      #if [ $annee -le 2003 ]; then
      #  continue
      #fi
      id=`echo $u | awk -F ";" '{print $1}'`
      url="$baseurl$detailspage$id"
      if ! test -e "tmp/dataset-$id.html"; then
        curl "$url" --connect-timeout 30 --retry 5 -s -S > "tmp/dataset-$id.html"
      fi
      if [ `grep -vc "adlibsearch_label_container_left" tmp/dataset-$id.html` -eq 0 ]; then
        curl "$url" --connect-timeout 30 --retry 5 -s -S > "tmp/dataset-$id.html"
      fi
      ct=0
      res="$url"
      grep '"adlibsearch_text_container_right' "tmp/dataset-$id.html" | sed 's#\s*<\/\?div[^>]*>\s*##g' | while read line; do
        case "$ct" in
          0) id=`echo $line | sed 's#/#-#g' | sed 's/[;\s ]\+/_/g'`
             if grep "|$id.pdf|" "$csvfile" > /dev/null; then
               continue
             fi
             res="$res|$id.pdf|$line";;
          3) for lang in "EN" "FR" "SP"; do
               pdfurl=`echo $line | sed 's#^.* href="\([^"]\+\)"[^>]*>\s*<img[^>]*>\s*'"$lang"'.*$#\1#'`
               if [ "$pdfurl" != "$line" ]; then
                 if ! [ -f "pdfs/$id.pdf" ] ; then
                   wget "$pdfurl" -qO "pdfs/$id.pdf"
                 fi
                 break
               fi
             done
             if [ "$pdfurl" == "$line" ]; then
               pdfurl=""
               lang=""
             fi
             res="$res|$pdfurl|$lang";;
          4) ;;
          6) ;;
         12) date=`echo $line | sed 's#^.* \([0-9]\+\)/\([0-9]\+\)/\([0-9]\{4\}\).*$#\3-\2-\1#'`
             echo "$res|$date|$annee" >> $csvfile;;
          *) line=`echo $line | sed 's/&8211;/–/g' | sed 's/&354;/Ń/g' | sed 's#\s*\(<[^>]*>\s*\)\+\s*#;#g' | sed 's/^[~-]$//' | sed 's/;$//' | sed 's/^;//' | sed 's/;,;/, /' | sed 's/; /, /g' | sed 's/\(\s*|\s*\)\+/ - /g'`
             res="$res|$line";;
        esac
        ct=$(($ct + 1))
      done
    done
  done
done

echo "Stats:" > $statsfile
echo "------" >> $statsfile
ct=1
for field in `echo $fields | sed 's/|/ /g'`; do
  if echo " $statsfields " | grep " $field " > /dev/null; then
    echo >> $statsfile
    echo " - $field:" >> $statsfile
    awk -F '|' '{print $'"$ct"'}' $csvfile | sed 's/;/\n/g' | sort | uniq -c | grep -v "1 $field" | sed 's/^\s*\([1-9]\) /   000\1 /' | sed 's/^\s*\([1-9][0-9]\) /   00\1 /' | sed 's/^\s*\([1-9][0-9][0-9]\) /   0\1 /' | sort -r >> $statsfile
  fi
  ct=$(($ct + 1))
done

