#!/bin/bash

#
# Demo hook for tools/services.sh
# runs after start and restart of restapi-dev,
# i.e. only on development systems (instance.standalone=1)
#
# path: services.d/<unit>/<action>-<NN>-<name>.sh
# action: start, stop, restart or any (any = start and restart)
# local hooks not in git: <action>-<NN>-<name>.local.sh
# disable a hook with: chmod -x <file>
# commands that need root: sudo -n <command> (never prompts, fails instead)
# output is only shown if the hook fails (exit code != 0)
#

echo "demo hook: action=$1 instance=$2 unit=$3 failed=$SERVICES_FAILED"

if systemctl is-active --quiet "$SERVICES_UNIT";
then
    echo "$SERVICES_UNIT is active"
else
    echo "$SERVICES_UNIT is not active"
    exit 1
fi
