#!/bin/bash

TARGET_FILE="$1"

if [ -z "$TARGET_FILE" ]; then
  echo "Usage: catclip <file>"
  exit 1
fi

if [ ! -f "$TARGET_FILE" ]; then
  echo "Error: File does not exist."
  exit 1
fi

OUTPUT=$(echo "==========================================="
echo "File: $TARGET_FILE"
echo "==========================================="
cat "$TARGET_FILE"
echo)

echo "$OUTPUT" | xclip -selection clipboard

echo "File content copied to clipboard."
