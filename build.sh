#!/usr/bin/env bash

# Remove old stuff.
printf "\nRemoving old build ...\n"
rm -rf ./build ./dist ./dblib.egg-info ./requirements.txt

printf "\nUpdating requirements.txt file ...\n"
pipreqs . --force --use-local

printf "\nBuilding wheel ...\n"
./setup.py sdist bdist_wheel

printf "\nSetup complete.\n\n"
