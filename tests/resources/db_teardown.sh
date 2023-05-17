#!/usr/bin/env bash
#-------------------------------------------------------------------------
# Prog:     db_teardown.sh
# Version:  0.1.0
# Desc:     Script wrapper for performing the post-testing database 
#           teardown operations.
#
# Use:      $ ./db_teardown.sh <db_test_user_pwd>
#
# Updates:
# 17.05.23  J. Berendt  Written.
#-------------------------------------------------------------------------

export MYSQL_PWD=$1
path=$( realpath $( dirname "$0" ) )
nargs=$#
user=testuser
dbname=dblib_test
host=localhost

declare -a scripts=("${path}/drop__all.sql")

# Main controller function.
function main() {
    # Perform pre-run checks.
    pre_checks
    # Run all scripts, regardless of exit status.
    for s in ${scripts[@]}; do
        call_mysql "${s}"
    done
    exit 0
}

# Execute the script using mysql.
function call_mysql() {
    script=$1
    mysql -u${user} -D${dbname} -h${host} < $script
    [[ $? -eq 0 ]] && printf "Complete: %s\n" $script
}

# Pre-run checks.
function pre_checks() {
    if [[ ${nargs} -ne 1 ]] ; then
        printf "\n[ERROR]: Number of expected args: 1. Received: %s.\n\n" ${nargs} >&2
        exit 1
    fi
}

main

