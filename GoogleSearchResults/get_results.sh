#!/bin/bash
# Usage : ./get_results.sh <list_keywords_file> [<N_results>] [<search_lang>] [<url_seeks_node>]
# Example : ./get_results.sh keywords.txt 200 http://seeks.fr
# Defaults to 100 results on http://localhost:8080

list=$1
n_results=100
lang="en"
seeknode="http://localhost:8080"

if [ -z "$list" ] || [ ! -f "$list" ]; then
  echo "Please specify a valid keyword list file"
  exit
fi

if [ ! -z "$2" ]; then
  n_results=$(($2 + 0))
fi
totalpages=$((($n_results - 1) / 100 + 1))
expansion=$(($totalpages + 1))

if [ ! -z "$3" ]; then
  lang=$3
fi

if [ ! -z "$4" ]; then
  seeknode=`echo $3 | sed 's#/\+$##'`
  testseeks=`curl -sL $seeknode | grep "seeks.git.sourceforge.net" | wc -l`
  if [ $testseeks -lt 1 ] || echo $seeknode | grep -v 'http://'; then
    echo "Please input a valid seek node url"
    exit
  fi
fi

seeks=`ps -ef | grep seeks | grep -v " grep " | wc -l`
if [ $seeks -lt 1 ]; then
  echo "Seeks is not running locally, please start it or add root url of seeks node, eg ./$0 $1 http://seeks.fr"
  exit
fi


if [ ! -f "$list.left" ]; then
  sed 's/\r//g' $list > $list.original
  cp $list.{original,left}
fi
mkdir -p json
touch $list.done

cat $list.left | while read line; do
  echo "Retrieving results for « $line »..."
  keyword=`echo $line | sed 's/ /+/g' | sed 's/"/%22/g'`
  for page in `seq $totalpages`; do
    echo " page $(($page))"
    curl -sL "$seeknode/search?output=json&rpp=100&page=$page&expansion=$expansion&prs=off&lang=$lang&q=$keyword" | sed 's/\(},\|\[\){/\1\n{/g' > json/$keyword-$page.json
    res=`grep '{"id":' json/$keyword-$page.json | wc -l`
    if [ $res -lt 1 ]; then
      if [ $page -eq 1 ]; then
        echo "WARNING: Google limit reached, please open a Google searchpage in a browser using proxy.medialab.sciences-po.fr:3128 as proxy and run captcha:"
        echo "FYI: error reached on query « $line » for results page number $page"
        echo "search-engine google http://www.google.com/search?q=$keyword&start=$(($page * 100))&num=100&hl=en&lr=en&ie=UTF-8&oe=UTF-8"
        exit
      fi
      break
    fi
    if [ $res -lt 85 ]; then
      break
    fi
    sec=$((10 + $RANDOM % 11))
    usec=$(($RANDOM % 10))
    sleep $sec.$usec
  done
  res=`grep '{"id":' json/$keyword-*.json | wc -l`
  echo "  -> $res results collected"
  echo $line >> $list.done
  grep -v "$line" $list.left > $list.todo
  mv $list.todo $list.left
done

if grep '<' $list.done $list.original > /dev/null ; then
  echo "All keywords searched and finished"
  echo "Results in json/"
  rm $list.done $list.original $list.left
else
  echo "Data collection is not finished"
  echo "Please restart script"
fi

