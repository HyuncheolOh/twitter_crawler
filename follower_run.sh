#!/bin/sh

echo "Crawl tweet followers"
python follower_search.py 2 & 
python follower_search.py 3 & 
python follower_search.py 4 & 
python follower_search.py 5 & 
python follower_search.py 6 & 
python follower_search.py 7 & 
python follower_search.py 8 & 
python follower_search.py 9 & 
python follower_search.py 10 & 
python follower_search.py 11 & 
python follower_search.py 12 & 
python follower_search.py 13 & 
python follower_search.py 14 & 
python follower_search.py 15 & 
python follower_search.py 16 & 
python origin_follower_search.py 17 & 

echo "Follower collection done"
 
WORK_PID=`jobs -l | awk '{print $2}'`
wait $WORK_PID
 
echo "Crawl tweet friends"

python friends_search.py 2 & 
python friends_search.py 3 & 
python friends_search.py 4 & 
python friends_search.py 5 & 
python friends_search.py 6 & 
python friends_search.py 7 & 
python friends_search.py 8 & 
python friends_search.py 9 & 
python friends_search.py 10 & 
python friends_search.py 11 & 
python friends_search.py 12 & 
python friends_search.py 13 & 
python friends_search.py 14 & 
python friends_search.py 15 & 
python friends_search.py 16 & 
python original_friends_search.py 17

echo "Friends collection done"
 
WORK_PID=`jobs -l | awk '{print $2}'`
wait $WORK_PID
 
