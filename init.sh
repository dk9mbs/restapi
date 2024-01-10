#/bin/bash

SCRIPTNAME=$BASH_SOURCE
BASEDIR=$(realpath $SCRIPTNAME)
BASEDIR=$(dirname $BASEDIR)
PLUGINPATH=$BASEDIR/plugins
FORMATTERPATH=$BASEDIR/formatter
VENV=$BASEDIR/venv/restapi

mkdir -p "$VENV"

echo "executing before hook files ..."
for FILE in $BASEDIR/init.d/B*.sh
do
    echo "execute before hook: $FILE"
   . $FILE
done
echo "hook files executed!"

if [ ! -f $VENV/bin/activate ];
then
    echo "virtual environment creating ($VENV) ..."
    python3 -m venv $VENV/
    echo "virtual environment created!"

    . $VENV/bin/activate

    echo "intalling $BASEDIR/requirements.txt with pip ..."
    pip  install --upgrade pip wheel setuptools
    pip install -r $BASEDIR/requirements.txt
    echo "all components installed!"
else
    echo "activating existing venv environment ($VENV) ..."
    . $VENV/bin/activate
fi

echo "---"
echo "=============================================================="
echo "\$0...............:$0"
echo "Scriptname.......:$SCRIPTNAME"
echo "Basedir..........:$BASEDIR"
echo "venv root........:$VENV"
echo "Plugindir........:$PLUGINPATH"
echo "=============================================================="

mkdir -p "$PLUGINPATH"
mkdir -p "$FORMATTERPATH"

export PYTHONPATH=$BASEDIR:$PLUGINPATH:$FORMATTERPATH:../:$(python $BASEDIR/cfgreader.py plugin root)
export RESTAPIPATH=$BASEDIR

echo "executing after hook files ..."
for FILE in $BASEDIR/init.d/A*.sh
do
    echo "execute after hook: $FILE"
   . $FILE
done
echo "after hook files executed!"

echo "=============================================================="
echo "PYTHONPATH........:$PYTHONPATH"
echo "RESTAPIPATH.......:$RESTAPIPATH"
echo "=============================================================="

