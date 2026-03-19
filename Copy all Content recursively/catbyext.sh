#!/bin/bash

TARGET_DIR="$1"
shift  # remove directory arg, keep extensions

EXTENSIONS=("$@")

if [ -z "$TARGET_DIR" ]; then
  echo "Usage: catall <directory> [extensions...]"
  exit 1
fi

cd "$TARGET_DIR" || exit 1

OUTPUT=$(find . -type f | sort | while read -r file; do

  # If extensions are provided
  if [ ${#EXTENSIONS[@]} -gt 0 ]; then
    for ext in "${EXTENSIONS[@]}"; do
      if [[ "$file" == *"$ext" ]]; then
        echo -e "\n==========================================="
        echo "File: $file"
        echo "==========================================="
        cat "$file"
        echo -e "\n"
        break
      fi
    done

  # Otherwise, fallback to text detection
  else
    if file "$file" | grep -q "text"; then
      echo -e "\n==========================================="
      echo "File: $file"
      echo "==========================================="
      cat "$file"
      echo -e "\n"
    fi
  fi

done)

echo "$OUTPUT" | xclip -selection clipboard

echo "All matching files are now in your clipboard."