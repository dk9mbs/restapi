#/bin/bash

VENV=~/venv/lab/bin/activate
PLUGINPATH=~/.restapi/plugins

SCRIPTNAME=$BASH_SOURCE
BASEDIR=$(realpath $SCRIPTNAME)
BASEDIR=$(dirname $BASEDIR)

echo "=============================================================="
echo "\$0...............:$0"
echo "Scriptname.......:$SCRIPTNAME"
echo "Basedir..........:$BASEDIR"
echo "=============================================================="

mkdir -p "$PLUGINPATH"

if [ -f "$VENV" ];
then
    echo "Activate venv environment"
    . $VENV
else
    echo "venv environment not found ($VENV)"
fi

export PYTHONPATH=/usr/local/restapi_plugins:~/.restapi/plugins:../:/tmp:$BASEDIR


