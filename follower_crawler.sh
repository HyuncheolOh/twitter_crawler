#!/bin/sh

while true; 

do 
	echo "Run follower crawler"
	sleep 1
	#repeat update per day
	#sleep 1000

	python follower_search.py
	python friends_search.py
	
	timestamp=`date +%Y%m%d%H%M`
	echo "$timestamp"
	echo "done"


done
