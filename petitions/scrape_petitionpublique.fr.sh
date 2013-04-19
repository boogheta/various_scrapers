#!/bin/bash

path=$(echo $0 | sed 's/[^\/]*$//')                                             
if [[ ! "$path" == "" ]]; then
  cd $path
fi

petid=$1
if [[ "$petid" == "" ]]; then
  petid="P2012N31899"
fi
echo $petid

url="http://www.petitionpublique.fr/PeticaoListaSignatarios.aspx?page=&pi=$petid&sr="
output="$petid.csv"
total=0
oldtotal=-1
i=0

echo "INDEX;NOM;COMMENTAIRE" > $output

while [ $total -gt $oldtotal ] ; do 
  oldtotal=$total
  i=$(($i + 1))
  j=$(($i*20 + 1))
  echo "$url$j"
  curl "$url$j" 2> /dev/null | grep "nowrap" | sed 's/<font color="Black">//g' | sed 's/<\/font>//g' | sed 's/\s\+<td>//' | sed 's/\(<[^>]*>\)\+/;/g' | perl -MHTML::Entities -ne 'binmode(STDOUT, ":utf8"); print decode_entities($_)' | sed 's/[  \s]*;[  \s]*/;/g' >> $output
  total=`wc -l $output | awk '{print $1}'`
  echo "$i ; $j ; $total ; $oldtotal"
done

echo "$total signataires stored in $output"

