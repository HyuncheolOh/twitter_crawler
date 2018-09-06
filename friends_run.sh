#!/bin/sh

echo  "예제를 시작합니다"

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
echo "모든 명령이 병렬로 실행되었습니다"
 
WORK_PID=`jobs -l | awk '{print $2}'`
wait $WORK_PID
 
echo "모든 명령이 종료되었습니다"
