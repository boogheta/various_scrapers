#!/bin/bash

APIKEY=
callflickr="curl -sL -X POST https://secure.flickr.com/services/rest/ -d api_key=$APIKEY -d format=json -d nojsoncallback=1"

