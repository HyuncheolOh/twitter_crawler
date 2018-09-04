#!/bin/sh

echo  "예제를 시작합니다"

python friends_search.py & 
python friends_search2.py & 
python friends_search3.py & 
python friends_search4.py & 
python friends_search5.py & 
python friends_search6.py & 
python friends_search7.py & 
python friends_search8.py & 
python friends_search9.py & 
python friends_search10.py & 
python friends_search11.py & 
python friends_search12.py & 
python friends_search13.py & 
python friends_search14.py & 


echo "모든 명령이 병렬로 실행되었습니다"
 
WORK_PID=`jobs -l | awk '{print $2}'`
wait $WORK_PID
 
echo "모든 명령이 종료되었습니다"
