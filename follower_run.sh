#!/bin/sh

echo  "예제를 시작합니다"
python follower_search.py & 
python follower_search2.py & 
python follower_search3.py & 
python follower_search4.py & 

python follower_search5.py & 
python follower_search6.py & 
python follower_search7.py & 
python follower_search8.py & 


python follower_search9.py & 
python follower_search10.py & 
python follower_search11.py & 
python follower_search12.py & 


echo "모든 명령이 병렬로 실행되었습니다"
 
WORK_PID=`jobs -l | awk '{print $2}'`
wait $WORK_PID
 
echo "모든 명령이 종료되었습니다"
