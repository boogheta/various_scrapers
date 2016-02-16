#!/bin/bash

curl -sL "http://www.integritywatch.eu/data/meeting_flat.csv" > TI_Commission_meetings.csv
curl -sL "http://www.integritywatch.eu/data/r.csv" > TI_Commission_guests.csv
./join_guests.py
