#!/bin/sh

python timeline_search.py 1&
python timeline_search.py 2&
python timeline_search.py 3&
python timeline_search.py 4&
python timeline_search.py 5&
python timeline_search.py 6&
python timeline_search.py 7&
python timeline_search.py 8&
python timeline_search.py 9&
python timeline_search.py 10&
python timeline_search.py 11&
python timeline_search.py 12&
python timeline_search.py 13&
python timeline_search.py 14&
python timeline_search.py 15&
 
WORK_PID=`jobs -l | awk '{print $2}'`
wait $WORK_PID
