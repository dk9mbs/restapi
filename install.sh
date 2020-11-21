#/bin/bash

. ./init.sh

INSTANCE_ID=$(python cfgreader.py instance id)
echo "$INSTANCE_ID"

#
# Create uwsgi.ini
#
mkdir -p /etc/restapi
chown -R www-data:www-data /etc/restapi

cat << EOF > /etc/restapi/uwsgi.$INSTANCE_ID.ini
# do not change this file here!
# auto created by init.sh
[uwsgi]
module = restapi:app

pythonpath = $BASEDIR
pythonpath = $PLUGINPATH
pythonpath = $(python cfgreader.py plugin root)
chdir = $BASEDIR
home = $VENV

master = true
processes = 1
#socket = 127.0.0.1:5000
#protocol = http
socket = /tmp/restapi.$INSTANCE_ID.sock
chmod-socket = 666
vacuum = true
uid = www-data
gid = www-data
die-on-term = true
EOF
#
# Create service
#
cat << EOF > /etc/systemd/system/restapi.$INSTANCE_ID.service
# do not change this file here!
# auto created by init.sh
[Unit]
Description=Restapi service
After=syslog.target

[Service]
ExecStart=$VENV/bin/uwsgi --ini /etc/restapi/uwsgi.$INSTANCE_ID.ini
# Requires systemd version 211 or newer
RuntimeDirectory=uwsgi
Restart=always
KillSignal=SIGQUIT
Type=notify
StandardError=syslog
NotifyAccess=all

[Install]
WantedBy=multi-user.target
EOF


systemctl daemon-reload
