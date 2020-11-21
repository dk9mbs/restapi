#/bin/bash

VENV=/var/venv/restapi
VENVALT=~/venv/lab

SCRIPTNAME=$BASH_SOURCE
BASEDIR=$(realpath $SCRIPTNAME)
BASEDIR=$(dirname $BASEDIR)
PLUGINPATH=$BASEDIR/plugins

#cd $BASEDIR
echo "---"
echo "=============================================================="
echo "\$0...............:$0"
echo "Scriptname.......:$SCRIPTNAME"
echo "Basedir..........:$BASEDIR"
echo "venv root........:$VENV"
echo "Plugindir........:$PLUGINPATH"
echo "=============================================================="

mkdir -p "$PLUGINPATH"

if [ -f "$VENV/bin/activate" ];
then
    echo "activate default venv environment ($VENV)"
    . $VENV/bin/activate
else
    echo "default venv environment not found ($VENV)"
    if [ -f "$VENVALT/bin/activate" ];
    then
        echo "activate alternative venv environment ($VENVALT)"
        . $VENVALT/bin/activate
    else
        echo "alternative venv environment not found ($VENVALT)"
    fi
fi

export PYTHONPATH=$BASEDIR:$PLUGINPATH:../:$(python $BASEDIR/cfgreader.py plugin root)
export RESTAPIPATH=$BASEDIR

echo "=============================================================="
echo "PYTHONPATH.......:$PYTHONPATH"
echo "=============================================================="
