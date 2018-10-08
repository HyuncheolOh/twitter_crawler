#!/bin/sh

echo "Crawl tweet followers"

python origin_follower_search.py 10 & 
python origin_follower_search.py 11 & 
python origin_follower_search.py 12 & 
python origin_follower_search.py 13 & 
python origin_follower_search.py 14 & 
python origin_follower_search.py 15 & 
python origin_follower_search.py 16 & 
python origin_follower_search.py 17 & 
python origin_follower_search.py 2 & 
python origin_follower_search.py 3 & 
python origin_follower_search.py 4 & 
python origin_follower_search.py 5 & 
python origin_follower_search.py 6 & 
python origin_follower_search.py 7 & 
python origin_follower_search.py 8 & 
python origin_follower_search.py 9 & 

echo "Follower collection done"
 
WORK_PID=`jobs -l | awk '{print $2}'`
wait $WORK_PID

