#!/bin/sh
[ -z "$1" ] && echo "Usage : Input Process .......... Please [scriptFileName ProcessName]" && exit

process_id=`ps -ax | grep "$1" | grep -vw "grep" | grep -vw $$ | awk '{print $1}'`

if [ -z "$process_id" ];then
	echo "+-------------------------------------------------------------+"
	echo "Not Found Process (입력하신 프로세스를 찾지 못했습니다.) ...... Done"
	echo "+-------------------------------------------------------------+"
	exit
else
	process_id_number=`ps -ax | grep "$1" | grep -vw "grep" | grep -vw $$ | awk '{print $1}'`

	for i in ${process_id_number} ;do
		kill -9 $i &> /dev/null
		printf "%-40s %-s\n" "$i PID Killed" "$(echo -ne "[ \\033[01;32m OK \\033[0m ]")"
	done
	sleep 2;
	echo "+-------------------------------------------------------------+"
	echo "Process Kill OK (프로세스가 강제적으로 종료 되었습니다.) ...... Done"
	echo "+-------------------------------------------------------------+"
fi

