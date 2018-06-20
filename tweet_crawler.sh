#!/bin/sh

while true; 

do 
	echo "Run tweet crawler"
	sleep 1

	python tweet_script.py
	
	timestamp=`date +%Y%m%d%H%M`
	echo "$timestamp"
	echo "done"

	#repeat update per day
	sleep 86400
done
