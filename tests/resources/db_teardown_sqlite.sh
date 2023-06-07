#!/usr/bin/env bash
#-------------------------------------------------------------------------
# Prog:     db_teardown_sqlite.sh
# Version:  0.1.0
# Desc:     Script wrapper for performing the post-testing SQLite database 
#           teardown operations.
#
# Use:      $ ./db_teardown_sqlite.sh <database_file.db>
#
# Updates:
# 06.07.23  J. Berendt  Written.
#-------------------------------------------------------------------------

dbpath="$1"
nargs=$#

# Main controller function.
function main() {
    # Perform pre-run checks.
    pre_checks
    # Delete the testing database file.
    delete_database_file
    exit $?
}

# Delete the testing database file.
function delete_database_file() {
    if [ -f ${dbpath} ] ; then
        rm ${dbpath}
        printf "Database file deleted: %s.\n" ${dbpath}
    fi
}

# Pre-run checks.
function pre_checks() {
    if [[ ${nargs} -ne 1 ]] ; then
        printf "\n[ERROR]: Number of expected args: 1. Received: %s.\n\n" ${nargs} >&2
        exit 1
    fi
}

main

