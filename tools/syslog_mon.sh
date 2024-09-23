SET_PLUGIN_STATUS=$(cat /var/log/syslog | grep "WAITING" -A0 -B0  | grep -c  'uwsgi')
DEADLOCK_ERROR=$(cat /var/log/syslog | grep "Deadlock" -A0 -B0  | grep -c  'uwsgi')
LOCK_TIMEOUT=$(cat /var/log/syslog | grep "pymysql.err.OperationalError: (1205, 'Lock wait timeout exceeded;" -A0 -B0  | grep -c  'python\[')

JSON="{\"sensor_id\":\"STATUS_ERROR\", \"sensor_value\": $SET_PLUGIN_STATUS, \"sensor_namespace\": \"restapi.monitoring\"}" 
echo "$JSON"

JSON="{\"sensor_id\":\"DEADLOCK_ERROR\", \"sensor_value\": $DEADLOCK_ERROR, \"sensor_namespace\": \"restapi.monitoring\"}"
echo "$JSON"

JSON="{\"sensor_id\":\"LOCK_TIMEOUT_ERROR\", \"sensor_value\": $LOCK_TIMEOUT, \"sensor_namespace\": \"restapi.monitoring\"}"
echo "$JSON"

