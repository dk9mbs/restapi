cat /var/log/syslog | grep "WAITING" -A0 -B0  | grep -c  'uwsgi'

SET_PLUGIN_STATUS=$(cat /var/log/syslog | grep "WAITING" -A0 -B0  | grep -c  'uwsgi')
DEADLOG=$(cat /var/log/syslog | grep "Deadlog" -A0 -B0  | grep -c  'uwsgi')

JSON="{\"STATUS_ERROR\": $SET_PLUGIN_STATUS, \"DEADLOG_ERROR\": $DEADLOG}"

echo "$JSON"
