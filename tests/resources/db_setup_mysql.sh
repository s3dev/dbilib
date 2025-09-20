#!/usr/bin/env bash
#-------------------------------------------------------------------------
# Prog:     db_setup_mysql.sh
# Version:  0.2.0
# Desc:     Script wrapper for performing the pre-testing MySQL database 
#           setup operations.
#
#           Notes:
#               - Before this script can be run, the database and testuser
#                 account must exist on the localhost. These can be 
#                 created by running the create_db_user.sql script on the
#                 database *as root*.
#
# Use:      $ ./db_setup_mysql.sh <db_test_user_pwd>
#
# Updates:
# 17.05.23  J. Berendt  Written.
# 07.06.23  J. Berendt  Updated for explicit MySQL support.
#-------------------------------------------------------------------------

export MYSQL_PWD=$1
path=$( realpath $( dirname "$0" ) )
path="${path}/mysql/setup/create"
nargs=$#
user=testuser
dbname=dbilib_test
host=localhost

# Any new scripts to be run are added here.
declare -a scripts=("${path}/create_table__guitars.sql" \
                    "${path}/create_table__players.sql" \
                    "${path}/create_view__v_guitars_fender.sql" \
                    "${path}/create_proc__sp_get_guitars_colour.sql" \
                    "${path}/create_proc__sp_insert_guitars_add_new.sql" \
                    "${path}/create_proc__sp_insert_players_add_new.sql" \
                    "${path}/create_proc__sp_update_guitars_colour.sql")

# Main controller function.
function main() {
    # Perform pre-run checks.
    pre_checks
    # Run all scripts.
    # Only run if previous script succeeds, else exit.
    for s in ${scripts[@]}; do
        if [[ $? -eq 0 ]]; then
            call_mysql "${s}"
        else
            printf "\nScript failed. Further processing aborted.\n\n" >&2
            exit 1
        fi
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

