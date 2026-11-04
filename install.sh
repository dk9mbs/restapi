#/bin/bash

#
# Install missing packets
#
sudo apt install python3.11-venv

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
mysql -u$MYSQL_USER -p$MYSQL_PASSWORD -h$MYSQL_HOST  $MYSQL_DATABASE < ./install/db/install.sql
echo "Install Database Objects $?"
mysql -u$MYSQL_USER -p$MYSQL_PASSWORD -h$MYSQL_HOST  $MYSQL_DATABASE < ./install/db/basedata.sql
echo "Import Data $?"

echo "------------------------------------------------------------"
echo "building the metadata cache ..."
python $BASEDIR/tools/metadata.py -u$RESTAPI_UID -p$RESTAPI_PWD
echo "metadata cache builded!"
echo "------------------------------------------------------------"

# execute after meta cache building
echo "Cleaning up the database ..."
mysql -u$MYSQL_USER -p$MYSQL_PASSWORD -h$MYSQL_HOST  $MYSQL_DATABASE < ./install/db/post_metacache.sql
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
sudo chown www-data:www-data /var/restapi/$INSTANCE_ID/spool

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

# ----------------------------------------------------------------- MCP BEGIN
#
# Create mcp service
# Eigenes venv, damit die Abhängigkeiten des MCP-SDK nicht mit restapi/uwsgi kollidieren
#
MCPVENV=$BASEDIR/venv/mcp
MCPREQFILE=$BASEDIR/install/python/mcp/requirements.txt
MCPENVFILE=/etc/restapi/mcp.$INSTANCE_ID.env

if [ ! -f $MCPVENV/bin/activate ];
then
    echo "mcp virtual environment creating ($MCPVENV) ..."
    python3 -m venv $MCPVENV/
    echo "mcp virtual environment created!"
fi
echo "installing $MCPREQFILE with pip ..."
$MCPVENV/bin/pip install --upgrade pip wheel setuptools
$MCPVENV/bin/pip install -r $MCPREQFILE
echo "mcp components installed!"

#
# Create mcp environment file (only once - contains the apikey!)
#
if [ ! -f $MCPENVFILE ];
then
echo "... writing $MCPENVFILE ..."
cat << EOF | sudo tee $MCPENVFILE > /dev/null
# Konfiguration für restapi-mcp.$INSTANCE_ID.service
# auto created by $BASEDIR/install.sh - wird nicht überschrieben

# restapi direkt über uwsgi (http-socket aus uwsgi.$INSTANCE_ID.ini)
DK9MBS_API_BASE=http://127.0.0.1:8881/api
# API-Key des MCP-Benutzers (id aus api_user_apikey)
DK9MBS_API_KEY=

# Schreibende Tools freigeben: 0 = ja, 1 = nur lesen
DK9MBS_READ_ONLY=1
# Optionale Einschränkung auf Tabellen (kommagetrennt), leer = Rechte laut api_group_permission
DK9MBS_TABLES=

# Transport hinter apache2
MCP_TRANSPORT=streamable-http
MCP_HOST=127.0.0.1
MCP_PORT=8765
MCP_PATH=/mcp
MCP_PUBLIC_HOST=dk9mbs.de
EOF
sudo chmod 600 $MCPENVFILE
else
    echo "$MCPENVFILE exists - not changed"
fi

echo "... writing restapi-mcp.service ..."
cat << EOF | sudo tee /etc/systemd/system/restapi-mcp.$INSTANCE_ID.service
# do not change this file here!
# auto created by $BASEDIR/install.sh
[Unit]
Description=restAPI mcp daemon
After=syslog.target network-online.target mysqld.service restapi.$INSTANCE_ID.service
Wants=network-online.target

[Service]
WorkingDirectory=$BASEDIR
EnvironmentFile=$MCPENVFILE
ExecStart=$MCPVENV/bin/python $BASEDIR/mcpservice.py
Restart=always
RestartSec=5
KillSignal=SIGTERM
Type=simple
User=www-data
Group=www-data
NoNewPrivileges=yes
PrivateTmp=yes
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "...reloading systemctl ..."
sudo systemctl daemon-reload
echo "*****************************************************************"
echo "API-Key eintragen:"
echo "------------------"
echo "sudo nano $MCPENVFILE"
echo ""
echo "start the service:"
echo "------------------"
echo "systemctl start restapi-mcp.$INSTANCE_ID.service"
echo ""
echo "autostart the service:"
echo "----------------------"
echo "systemctl enable restapi-mcp.$INSTANCE_ID.service"
echo ""
echo "logs:"
echo "-----"
echo "journalctl -u restapi-mcp.$INSTANCE_ID.service -f"
echo "*****************************************************************"
# ----------------------------------------------------------------- MCP END


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
