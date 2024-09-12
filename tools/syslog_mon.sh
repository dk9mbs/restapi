SET_PLUGIN_STATUS=$(cat /var/log/syslog | grep "WAITING" -A0 -B0  | grep -c  'uwsgi')
DEADLOCK_ERROR=$(cat /var/log/syslog | grep "Deadlock" -A0 -B0  | grep -c  'uwsgi')

JSON="{\"STATUS_ERROR\": $SET_PLUGIN_STATUS, \"DEADLOCK_ERROR\": $DEADLOCK_ERROR}"

echo "$JSON"
