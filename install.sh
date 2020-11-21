#/bin/bash

. ./init.sh

#
# Create uwsgi.ini
#
cat << EOF > uwsgi.ini
# do not change this file here!
# auto created by init.sh
[uwsgi]
module = restapi:app

pythonpath = $PLUGINPATH
chdir = $BASEDIR
home = $VENV

master = true
processes = 5
#socket = 127.0.0.1:5000
#protocol = http
socket = /tmp/restapi.sock
chmod-socket = 666
vacuum = true
uid = www-data
gid = www-data
die-on-term = true
EOF
#
# Create service
#
cat << EOF > /etc/systemd/system/restapi.service
# do not change this file here!
# auto created by init.sh
[Unit]
Description=Restapi service
After=syslog.target

[Service]
ExecStart=$VENV/bin/uwsgi --ini $BASEDIR/uwsgi.ini
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

