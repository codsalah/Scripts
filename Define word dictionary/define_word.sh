#!/bin/bash

# Get the word from the clipboard
word=$(xclip -o -selection primary)

# Fetch the dictionary data for the word from the API
query=$(curl -s "https://api.dictionaryapi.dev/api/v2/entries/en_US/$word")

# Check if the query is empty (i.e., invalid word)
[ -z "$query" ] && notify-send -h string:bgcolor:#bf616a -t 3000 "Invalid word." && exit 0

# Extract the first 3 definitions from the response
def=$(echo "$query" | jq -r '[.[].meanings[].definitions[] | {pos: .partOfSpeech, def: .definition}] | .[:3] | .[] | "\n\(.pos). \(.def)"')

# Append the word and definitions to the file
echo -e "## $word\n$def\n" >> /put/your/path/to/the/file/here/English_Dictionary.md

# Display the definitions in a notification (optional, remove if not needed)
notify-send -t 60000 "$word -" "$def"