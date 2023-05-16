#!/usr/bin/env bash

# Remove old stuff.
printf "\nRemoving old build ...\n"
rm -rf ./build ./dist ./dblib.egg-info

printf "\nUpdating requirements.txt file ...\n"
pipreqs . --force

printf "\nBuilding wheel ...\n"
./setup.py bdist_wheel

printf "\nSetup complete.\n\n"
