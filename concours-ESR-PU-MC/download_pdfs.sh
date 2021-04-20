#!/bin/bash

mkdir -p pdfs

for url in https://www.galaxie.enseignementsup-recherche.gouv.fr/ensup/CNU_qualification.htm https://www.galaxie.enseignementsup-recherche.gouv.fr/ensup/cand_resultats_qualification.htm; do
 curl -sL "$url" |
  grep "\.pdf.*qualifié"  |
  while read line; do
   pdfurl="https://www.galaxie.enseignementsup-recherche.gouv.fr/ensup/"$(echo $line | sed -r 's/^.*(<a .*Liste des qualifiés[^<]*<\/a>).*$/\1/' | awk -F '"' '{print $2}')
   pdftitle=$(echo $line | sed 's/^.*Liste des qualifiés //' | sed 's/<.*$//')
   annee=$(echo $pdftitle | awk '{print $1}')
   typ="PU"
   extra=""
   if echo $pdftitle | grep "conférences" > /dev/null; then
    typ="MC"
   fi
   if echo $pdftitle | grep "Muséum" > /dev/null; then
    extra="-MNHN"
   fi
   pdffile="${annee}-qualifies-${typ}${extra}.pdf"
   echo "Downloading $pdffile at $pdfurl ..."
   wget --quiet "$pdfurl" -O pdfs/"$pdffile"
  done
done

