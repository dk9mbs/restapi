#/bin/bash

. ./init.sh

#
# Read the id of the instance from the local config.py file
# by example dev, test or prod
#
INSTANCE_ID=$(python $BASEDIR/cfgreader.py instance id)
echo "$INSTANCE_ID"

mkdir -p $BASEDIR/plugin
mkdir -p $BASEDIR/3thparty
#
# create the spool directory for the uwsgi task
# the spool is only needed in case of using uwsgi
#
sudo mkdir -p /var/restapi/$INSTANCE_ID/spool
sudo chown www-data.www-data /var/restapi/$INSTANCE_ID/spool

#
# Create uwsgi.ini
#
sudo mkdir -p /etc/restapi
#sudo chown -R www-data:www-data /etc/restapi

echo "... writing uwsgi.ini ..."
cat << EOF | sudo tee /etc/restapi/uwsgi.$INSTANCE_ID.ini
# do not change this file here!
# auto created by $BASEDIR/install.sh
[uwsgi]
module = restapi:app

pythonpath = $BASEDIR
pythonpath = $PLUGINPATH
pythonpath = $(python $BASEDIR/cfgreader.py plugin root)
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

#spooler=/tmp/spool
spooler=/var/restapi/$INSTANCE_ID/spool
import = task

EOF
#
# Create service
#
echo "... writing restapi.service ..."
cat << EOF | sudo tee /etc/systemd/system/restapi.$INSTANCE_ID.service
# do not change this file here!
# auto created by $BASEDIR/install.sh
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

echo "...reloading systemctl ..."
sudo systemctl daemon-reload

echo "ready!"
