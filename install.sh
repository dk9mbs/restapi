#/bin/bash

. ./init.sh

#
# Read the id of the instance from the local config.py file
# by example dev, test or prod
#
INSTANCE_ID=$(python $BASEDIR/cfgreader.py instance id)

MYSQL_USER=$(python $BASEDIR/cfgreader.py mysql user)
MYSQL_PASSWORD=$(python $BASEDIR/cfgreader.py mysql password)
MYSQL_DATABASE=$(python $BASEDIR/cfgreader.py mysql database)
MYSQL_HOST=$(python $BASEDIR/cfgreader.py mysql host)
RESTAPI_UID=$1
RESTAPI_PWD=$2

echo "Instance         $INSTANCE_ID"
echo "mysql User       $MYSQL_USER"
echo "mysql password   *******"
echo "mysql databse    $MYSQL_DATABASE"
echo "mysql host       $MYSQL_HOST"

mysql -u$MYSQL_USER -p$MYSQL_PASSWORD -h$MYSQL_HOST -e"CREATE DATABASE IF NOT EXISTS $MYSQL_DATABASE;"
mysql -u$MYSQL_USER -p$MYSQL_PASSWORD -h$MYSQL_HOST  $MYSQL_DATABASE < ./install/install.sql
echo "Install Database Objects $?"
mysql -u$MYSQL_USER -p$MYSQL_PASSWORD -h$MYSQL_HOST  $MYSQL_DATABASE < ./install/basedata.sql
echo "Import Data $?"

echo "------------------------------------------------------------"
echo "building the metadata cache ..."
python $BASEDIR/tools/metadata.py -u$RESTAPI_UID -p$RESTAPI_PWD
echo "metadata cache builded!"
echo "------------------------------------------------------------"

# execute after meta cache building
mysql -u$MYSQL_USER -p$MYSQL_PASSWORD -h$MYSQL_HOST  $MYSQL_DATABASE < ./install/post_metacache.sql
echo "CleanUp Database $?"

mkdir -p $BASEDIR/plugins
mkdir -p $BASEDIR/formatter
mkdir -p $BASEDIR/3thparty
mkdir -p $BASEDIR/wwwroot/portal
mkdir -p $BASEDIR/wwwroot/templates/solutions
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
pythonpath = $FORMATTERPATH
pythonpath = $(python $BASEDIR/cfgreader.py plugin root)
chdir = $BASEDIR
home = $VENV

master = true
processes = 10
#socket = 127.0.0.1:5000
#protocol = http

# use socket for nginx
#socket = /tmp/restapi.$INSTANCE_ID.sock

# use http-socket for apache2
http-socket = :8881

chmod-socket = 666
vacuum = true
uid = www-data
gid = www-data
die-on-term = true

# spooler is deprecated.
# for periodic tasks use the timeservice
#spooler=/var/restapi/$INSTANCE_ID/spool
#import = task
# end spooler

EOF
#
# Create restapi uwsgi service
#
echo "... writing restapi.service ..."
cat << EOF | sudo tee /etc/systemd/system/restapi.$INSTANCE_ID.service
# do not change this file here!
# auto created by $BASEDIR/install.sh
[Unit]
Description=Restapi service
After=syslog.target mysqld.service

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


#
# Create restapi-dev
#
echo "... writing restapi-dev.service ..."
cat << EOF | sudo tee /etc/systemd/system/restapi-dev.$INSTANCE_ID.service
# do not change this file here!
# auto created by $BASEDIR/install.sh
[Unit]
Description=restAPI standalone daemon
After=syslog.target mysqld.service

[Service]
WorkingDirectory=$BASEDIR
Environment="PYTHONPATH=$PYTHONPATH"
ExecStart=$VENV/bin/python $BASEDIR/restapi.py
Restart=always
KillSignal=SIGQUIT
Type=idle
StandardError=syslog
NotifyAccess=all

[Install]
WantedBy=multi-user.target
EOF


#
# Create timerservice
#
echo "... writing restapi-timer.service ..."
cat << EOF | sudo tee /etc/systemd/system/restapi-timer.$INSTANCE_ID.service
# do not change this file here!
# auto created by $BASEDIR/install.sh
[Unit]
Description=restAPI timer daemon
After=syslog.target mysqld.service

[Service]
WorkingDirectory=$BASEDIR
Environment="PYTHONPATH=$PYTHONPATH"
ExecStart=$VENV/bin/python $BASEDIR/timerservice.py
Restart=always
KillSignal=SIGQUIT
Type=idle
StandardError=syslog
NotifyAccess=all

[Install]
WantedBy=multi-user.target
EOF


#
# Create message service
#
echo "... writing restapi-msg.service ..."
cat << EOF | sudo tee /etc/systemd/system/restapi-msg.$INSTANCE_ID.service
# do not change this file here!
# auto created by $BASEDIR/install.sh
[Unit]
Description=restAPI message daemon
After=syslog.target mysqld.service

[Service]
WorkingDirectory=$BASEDIR
Environment="PYTHONPATH=$PYTHONPATH"
ExecStart=$VENV/bin/python $BASEDIR/msgservice.py
Restart=always
KillSignal=SIGQUIT
Type=idle
StandardError=syslog
NotifyAccess=all

[Install]
WantedBy=multi-user.target
EOF

echo "...reloading systemctl ..."
sudo systemctl daemon-reload
echo "*****************************************************************"
echo "start the services:"
echo "-------------------"
echo "systemctl start restapi-dev.$INSTANCE_ID.service"
echo "systemctl start restapi-timer.$INSTANCE_ID.service"
echo "systemctl start restapi-msg.$INSTANCE_ID.service"
echo ""
echo ""
echo "autostart the services:"
echo "-----------------------"
echo "systemctl enable restapi-dev.$INSTANCE_ID.service"
echo "systemctl enable restapi-timer.$INSTANCE_ID.service"
echo "systemctl enable restapi-msg.$INSTANCE_ID.service"
echo "*****************************************************************"

echo "ready!"
