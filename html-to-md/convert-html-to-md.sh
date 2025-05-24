#!/usr/bin/env bash
set -euo pipefail

# 1. Prerequisites check
command -v pandoc >/dev/null || { echo >&2 "Error: pandoc is not installed."; exit 1; }

# 2. Find & convert
echo "🔍 Finding HTML files and converting to Markdown..."
find . -type f -name '*.html' \
  ! -path './cdn-cgi/*' \
  ! -path './static/*' \
  -print0 \
| while IFS= read -r -d '' html; do
    md="${html%.html}.md"
    echo "  • $html → $md"
    pandoc \
      "$html" \
      -f html \
      -t gfm \
      --wrap=preserve \
      -o "$md"
    rm "$html"  ###################################################### Delete original HTML file 
done

# 3. Fix up any internal links pointing to .html
echo "Rewriting internal links (.html → .md)..."
grep -Rl "\.html" . --include="*.md" \
  | xargs sed -i.bak -E 's/\]\(([^)]+)\.html(\#[^)]+)?\)/](\1.md\2)/g'

# 4. Clean up backup files from sed
find . -type f -name '*.bak' -delete

echo "Conversion complete! All .html files converted and removed. .md files are ready."
