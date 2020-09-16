#/bin/bash



VENV=~/venv/restapi/bin/activate
VENVALT=~/venv/lab/bin/activate
PLUGINPATH=~/.restapi/plugins

SCRIPTNAME=$BASH_SOURCE
BASEDIR=$(realpath $SCRIPTNAME)
BASEDIR=$(dirname $BASEDIR)

echo "=============================================================="
echo "\$0...............:$0"
echo "Scriptname.......:$SCRIPTNAME"
echo "Basedir..........:$BASEDIR"
export PYTHONPATH=$BASEDIR:~/.restapi/plugins:../:/tmp
export RESTAPIPATH=$BASEDIR

echo "PYTHONPATH.......:$PYTHONPATH"
echo "=============================================================="

mkdir -p "$PLUGINPATH"

if [ -f "$VENV" ];
then
    echo "activate default venv environment ($VENV)"
    . $VENV
else
    echo "default venv environment not found ($VENV)"
    if [ -f "$VENVALT" ];
    then
        echo "activate alternative venv environment ($VENVALT)"
        . $VENVALT
    else
        echo "alternative venv environment not found ($VENVALT)"
    fi
fi


