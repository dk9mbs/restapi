#!/bin/bash

#
# Start, stop or restart all systemd units of this restapi instance
# usage: tools/services.sh start|stop|restart
#
# The instance id (dev, test, prod ...) is read from config.py.
# instance.standalone=1 (development system) manages restapi-dev
# instead of restapi, default is 0.
#
# Hooks: after the action the executable scripts in
# tools/services.d/<unit>/<action>-<NN>-<name>.sh are run for every unit
# whose action succeeded. any-<NN>-<name>.sh runs after start and restart.
# Hooks named *.local.sh are not in git. See services.d/restapi-dev/any-90-demo.sh
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

HOOKDIR="$BASEDIR/tools/services.d"

# no colors, no carriage return and no password prompt without a terminal (cron)
if [ -t 1 ];
then
    TTY=1
    CR="\r"
    GREEN="\e[32m"
    RED="\e[31m"
    RESET="\e[0m"
else
    TTY=0
    CR=""
    GREEN=""
    RED=""
    RESET=""
fi

SUDO=""
if [ "$(id -u)" -ne 0 ];
then
    SUDO="sudo"
    if [ $TTY -eq 1 ];
    then
        # ask for the password before the animation starts
        sudo -v || exit 1
    elif ! sudo -n -v 2>/dev/null;
    then
        echo "ERROR: services.sh needs root or passwordless sudo when run without a terminal"
        exit 1
    fi
fi

SPINNER='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'

#
# Runs a command in the background and animates the first character of the line,
# the output of the command is only shown if it fails
# usage: [PREFIX=<prefix>] run_with_spinner <text> <command> [args...]
#
run_with_spinner() {
    local text=$1
    local prefix=${PREFIX:-}
    local indent="    ${prefix//?/ }"
    shift
    local log
    log=$(mktemp)

    "$@" </dev/null >"$log" 2>&1 &
    local pid=$!

    if [ $TTY -eq 1 ];
    then
        local i=0
        tput civis 2>/dev/null
        while kill -0 $pid 2>/dev/null; do
            printf "\r%s%s %s" "$prefix" "${SPINNER:$i:1}" "$text"
            i=$(( (i+1) % ${#SPINNER} ))
            sleep 0.1
        done
        tput cnorm 2>/dev/null
    fi

    wait $pid
    local rc=$?

    if [ $rc -eq 0 ];
    then
        printf "${CR}%s${GREEN}✔${RESET} %s\n" "$prefix" "$text"
    else
        printf "${CR}%s${RED}✘${RESET} %s\n" "$prefix" "$text"
        sed "s/^/$indent/" "$log"
    fi

    rm -f "$log"
    return $rc
}

#
# Prints the executable hooks of a unit for the current action, in execution order
# usage: list_hooks <unit>
#
list_hooks() {
    local dir="$HOOKDIR/${1%.$INSTANCE_ID.service}"
    local prefixes=("$ACTION")
    local prefix file

    [ -d "$dir" ] || return 0
    [ "$ACTION" != "stop" ] && prefixes+=("any")

    for prefix in "${prefixes[@]}"; do
        for file in "$dir/$prefix"-[0-9][0-9]-*.sh; do
            [ -f "$file" ] && [ -x "$file" ] || continue
            [[ "$(basename "$file")" == *" "* ]] && continue
            echo "$file"
        done
    done
}

#
# Runs one hook in the repo root
# usage: exec_hook <file> <unit>
#
exec_hook() {
    cd "$BASEDIR" && SERVICES_UNIT=$2 "$1" "$ACTION" "$INSTANCE_ID" "$2"
}

trap 'tput cnorm 2>/dev/null; echo; exit 130' INT TERM

echo "Instance: $INSTANCE_ID ($MODE)"

if systemctl is-active --quiet "$OTHER_API_UNIT";
then
    printf "${RED}!${RESET} %s is running but not managed in %s mode\n" "$OTHER_API_UNIT" "$MODE"
fi

ERRORS=0
declare -A UNIT_OK
for unit in "${UNITS[@]}"; do
    if run_with_spinner "$ACTION $unit" $SUDO systemctl "$ACTION" "$unit";
    then
        UNIT_OK[$unit]=1
    else
        ERRORS=$((ERRORS+1))
    fi
done

export SERVICES_ACTION=$ACTION
export SERVICES_INSTANCE_ID=$INSTANCE_ID
export SERVICES_MODE=$MODE
export SERVICES_API_UNIT=$API_UNIT
export SERVICES_UNITS="${UNITS[*]}"
export SERVICES_FAILED=$ERRORS
export SERVICES_BASEDIR=$BASEDIR

HOOK_ERRORS=0
HOOK_PREFIX="↳ "
export LC_COLLATE=C
for unit in "${UNITS[@]}"; do
    while IFS= read -r hook; do
        name="${unit%.$INSTANCE_ID.service}/$(basename "$hook")"
        if [ -z "${UNIT_OK[$unit]}" ];
        then
            echo "$HOOK_PREFIX- hook $name (skipped, unit failed)"
        else
            PREFIX=$HOOK_PREFIX run_with_spinner "hook $name" exec_hook "$hook" "$unit" || HOOK_ERRORS=$((HOOK_ERRORS+1))
        fi
    done < <(list_hooks "$unit")
done

if [ $ERRORS -ne 0 ] || [ $HOOK_ERRORS -ne 0 ];
then
    SUMMARY=""
    [ $ERRORS -ne 0 ] && SUMMARY="$ERRORS unit(s) failed"
    [ $HOOK_ERRORS -ne 0 ] && SUMMARY="${SUMMARY:+$SUMMARY, }$HOOK_ERRORS hook(s) failed"
    echo "$SUMMARY"
    exit 1
fi
