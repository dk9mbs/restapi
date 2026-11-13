#!/bin/bash

#
# Start, stop or restart all systemd units of this restapi instance
# usage: tools/services.sh start|stop|restart
#
# The instance id (dev, test, prod ...) is read from config.py.
# instance.standalone=1 (development system) manages restapi-dev
# instead of restapi, default is 0.
#

if [ "$1" != "start" ] && [ "$1" != "stop" ] && [ "$1" != "restart" ];
then
    echo "usage: $0 start|stop|restart"
    exit 1
fi
ACTION=$1

BASEDIR=$(dirname "$(dirname "$(readlink -f "$0")")")

INSTANCE_ID=$(cd "$BASEDIR" && python3 cfgreader.py instance id)
if [ $? -ne 0 ] || [ -z "$INSTANCE_ID" ];
then
    echo "ERROR: cannot read instance id from $BASEDIR/config.py"
    exit 1
fi

# standalone=1 (development system): restapi-dev (flask dev server) instead of restapi (uwsgi)
STANDALONE=$(cd "$BASEDIR" && python3 cfgreader.py instance standalone 0)
if [ "$STANDALONE" == "1" ];
then
    API_UNIT="restapi-dev.$INSTANCE_ID.service"
    OTHER_API_UNIT="restapi.$INSTANCE_ID.service"
    MODE="standalone"
elif [ "$STANDALONE" == "0" ];
then
    API_UNIT="restapi.$INSTANCE_ID.service"
    OTHER_API_UNIT="restapi-dev.$INSTANCE_ID.service"
    MODE="uwsgi"
else
    echo "ERROR: invalid value '$STANDALONE' for instance.standalone in $BASEDIR/config.py (allowed: 0 or 1)"
    exit 1
fi

UNITS=(
    "$API_UNIT"
    "restapi-msg.$INSTANCE_ID.service"
    "restapi-mcp.$INSTANCE_ID.service"
    "restapi-timer.$INSTANCE_ID.service"
)

# stop in reverse order: restapi-mcp depends on restapi
if [ "$ACTION" == "stop" ];
then
    for (( i=${#UNITS[@]}-1; i>=0; i-- )); do
        REVERSED+=("${UNITS[$i]}")
    done
    UNITS=("${REVERSED[@]}")
fi

SUDO=""
if [ "$(id -u)" -ne 0 ];
then
    SUDO="sudo"
    # ask for the password before the animation starts
    sudo -v || exit 1
fi

GREEN="\e[32m"
RED="\e[31m"
RESET="\e[0m"
SPINNER='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'

#
# Runs systemctl for one unit and animates the first character of the line
# usage: run_unit <unit>
#
run_unit() {
    local unit=$1
    local text="$ACTION $unit"
    local log
    log=$(mktemp)

    $SUDO systemctl "$ACTION" "$unit" >"$log" 2>&1 &
    local pid=$!

    if [ -t 1 ];
    then
        local i=0
        tput civis 2>/dev/null
        while kill -0 $pid 2>/dev/null; do
            printf "\r%s %s" "${SPINNER:$i:1}" "$text"
            i=$(( (i+1) % ${#SPINNER} ))
            sleep 0.1
        done
        tput cnorm 2>/dev/null
    fi

    wait $pid
    local rc=$?

    if [ $rc -eq 0 ];
    then
        printf "\r${GREEN}✔${RESET} %s\n" "$text"
    else
        printf "\r${RED}✘${RESET} %s\n" "$text"
        sed 's/^/    /' "$log"
    fi

    rm -f "$log"
    return $rc
}

trap 'tput cnorm 2>/dev/null; echo; exit 130' INT TERM

echo "Instance: $INSTANCE_ID ($MODE)"

if systemctl is-active --quiet "$OTHER_API_UNIT";
then
    printf "${RED}!${RESET} %s is running but not managed in %s mode\n" "$OTHER_API_UNIT" "$MODE"
fi

ERRORS=0
for unit in "${UNITS[@]}"; do
    run_unit "$unit" || ERRORS=$((ERRORS+1))
done

if [ $ERRORS -ne 0 ];
then
    echo "$ERRORS unit(s) failed"
    exit 1
fi
