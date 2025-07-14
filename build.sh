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

cat << EOF >> requirements.txt

# Manual additions:
importlib_metadata>=8.0.0
pyodbc>=5.0.0
zipp>=3.19.1

EOF

# Package it!
python -m build --wheel --sdist --installer pip

# Notification(s)
printf "\nBuild complete.\n\n"

