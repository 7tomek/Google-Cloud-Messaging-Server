#!bin/sh

echo Client Open-RnD GCM

if [ "$1" == "--help" ]; then
   echo "Usage: `basename $0` [--host=<host> --data=<data> --type=[REG|DEL|IDS|SEND]]"
   exit 0
fi

HOST=""
DATA=""
TYPE=""

for arg in "$@"
do
case $arg in
	-h=*|--host=*)
	HOST="${arg#*=}"
	;;
	-d=*|--data=*)
	DATA="${arg#*=}"
	;;
	-t=*|--type=*)
	TYPE="${arg#*=}"
	;;
	--default)
	DEFAULT=YES
	;;
	*)
	;;
esac
done

echo Setup parameters --host=${HOST} --data=${DATA} --type=${TYPE}

fun_type() {
if [ -z != $TYPE ]
then
	if [ $TYPE == "REG" ]
	then
		echo REGISTRATION_ID = ${DATA}
		msg="{\"reg_id\":\"$DATA\"}" 
		curl -H "Content-Type: application/json" -X POST -d "$msg" $HOST/register	
	elif [ $TYPE == "DEL" ]
	then
		echo DELETE_ID = ${DATA}
		msg="{\"reg_id\":\"$DATA\"}" 
		curl -H "Content-Type: application/json" -X POST -d "$msg" $HOST/delete
	elif [ $TYPE == "IDS" ]
	then
		echo IDS
		curl -H "Content-Type: application/json" -X POST $HOST/ids

	elif [ $TYPE == "SEND" ]
	then
		echo SEND_MESSAGE = ${DATA}
		msg="{\"msg\":\"$DATA\"}" 
		curl -H "Content-Type: application/json" -X POST -d "$msg" $HOST/send
	fi
else
	echo "Usage: `basename $0` [--type=[...]] is mandatory"	
fi
}

if [ -z != $HOST ]
then
	fun_type	
else
	echo "Usage: `basename $0` [--host=<host>] is mandatory"
fi


