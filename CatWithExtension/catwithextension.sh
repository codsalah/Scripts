#!/bin/bash

# Usage check
if [ -z "$1" ]; then
    echo "Usage: $0 <extension>"
    exit 1
fi

# Remove leading dot if provided
EXT="${1#.}"

# Find all files recursively in the current directory
find "$PWD" -type f -name "*.$EXT" | while read -r f; do
    echo "-------------------------- [[ FILE $(basename "$f") ]]  --------------------------"
    cat "$f"
    echo
done
