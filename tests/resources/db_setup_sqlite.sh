#!/usr/bin/env bash
#-------------------------------------------------------------------------
# Prog:     db_setup_sqlite.sh
# Version:  0.1.0
# Desc:     Script wrapper for performing the pre-testing SQLite database 
#           setup operations.
#
# Use:      $ ./db_setup_sqlite.sh <database_file.db>
#
# Updates:
# 07.06.23  J. Berendt  Written.
#-------------------------------------------------------------------------

dbpath="$1"
path=$( realpath $( dirname "$0" ) )
path="${path}/sqlite/setup/create"
nargs=$#
host=localhost

# Any new scripts to be run are added here.
declare -a scripts=("${path}/create_table__guitars.sql")

# Main controller function.
function main() {
    # Perform pre-run checks.
    pre_checks
    # Run all scripts.
    # Only run if previous script succeeds, else exit.
    for s in ${scripts[@]}; do
        if [[ $? -eq 0 ]]; then
            call_sqlite "${s}"
        else
            printf "\nScript failed. Further processing aborted.\n\n" >&2
            exit 1
        fi
    done
    exit 0
}

# Execute the script using sqlite3.
function call_sqlite() {
    script=$1
    sqlite3 ${dbpath} < $script
    [[ $? -eq 0 ]] && printf "Complete: %s\n" $( basename $script )
}

# Pre-run checks.
function pre_checks() {
    if [[ ${nargs} -ne 1 ]] ; then
        printf "\n[ERROR]: Number of expected args: 1. Received: %s.\n\n" ${nargs} >&2
        exit 1
    else
        [ -f ${dbpath} ] || touch ${dbpath}
    fi
}

main

