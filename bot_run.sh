#!/bin/sh

echo  "예제를 시작합니다"

python bot_search.py 2 & 
python bot_search.py 3 & 
python bot_search.py 4 & 
python bot_search.py 5 & 
python bot_search.py 6 & 
python bot_search.py 7 & 
python bot_search.py 8 & 
python bot_search.py 9 & 
python bot_search.py 10 & 
python bot_search.py 11 & 
python bot_search.py 12 & 
python bot_search.py 13 & 
python bot_search.py 14 & 
python bot_search.py 15 & 
python bot_search.py 16 & 
python bot_search.py 17
echo "모든 명령이 병렬로 실행되었습니다"
 
WORK_PID=`jobs -l | awk '{print $2}'`
wait $WORK_PID
 
echo "모든 명령이 종료되었습니다"
