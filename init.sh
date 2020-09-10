#/bin/bash

BASEDIR=$(realpath $0)
BASEDIR=$(dirname $BASEDIR)
echo "====================="
echo "$BASEDIR"
echo "====================="

mkdir -p ~/.restapi/plugins
#mkdir -p /usr/local/restapi_plugins


. ~/venv/lab/bin/activate
export PYTHONPATH=/usr/local/restapi_plugins:~/.restapi/plugins:../:/tmp


