#!/bin/bash

. ../init.sh

export PYTHONPATH=$PYTHONPATH:/tmp

echo "PYTHONPATH: $PYTHONPATH"

cat << EOF > /tmp/plugin_test.py
def execute(context, plugin_context, params):
    print("===== START OF PLUGIN =====")
    print(f"publisher.: {plugin_context['publisher']}")
    print(f"trigger...: {plugin_context['trigger']}")
    print(f"type......: {plugin_context['type']}")
    print(f"cancel....: {plugin_context['cancel']}")
    params['name']="GD77"
    plugin_context['cancel']=True
    print("===== END OF PLUGIN =====")
EOF



python -m unittest discover
