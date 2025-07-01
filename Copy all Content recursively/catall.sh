#!/bin/bash

TARGET_DIR="$1"

if [ -z "$TARGET_DIR" ]; then
  echo "Usage: catall <directory>"
  exit 1
fi

cd "$TARGET_DIR" || exit 1

# Collect all text files' content into a variable
OUTPUT=$(find . -type f | sort | while read -r file; do
  if file "$file" | grep -q "text"; then
    echo -e "\n==========================================="
    echo "File: $file"
    echo "==========================================="
    cat "$file"
    echo -e "\n"  # Add a newline after each file
  fi
done)

# Send the collected content to clipboard
echo "$OUTPUT" | xclip -selection clipboard

# Success message
echo "All text files' content (recursively) is now in your clipboard."
