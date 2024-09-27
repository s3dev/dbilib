#!/usr/bin/env bash

pkg="dbilib"
dirs="./build ./dist ./${pkg}.egg-info"

printf "\n| --- Building %s --- |\n" $pkg

# Check for existing dist/build directories and delete them.
printf "\nChecking for existing build directories ...\n"
for d in ${dirs}; do
    if [ -d "${d}" ]; then
        printf "|- Deleting %s\n" "${d}"
        rm -rf "${d}"
    fi
done
printf "\n"

# Get requirements.
preqs . --replace  # Force a replacement if needed.

# Package it!
python -m build --wheel --sdist --installer pip

# Notification(s)
printf "\nBuild complete.\n\n"
printf "Reminders:\n  - Add mysql-connector-python to the requirements file\n\n"
