# HTML to Markdown
### 📝 convert-html-to-md.sh

A simple Bash script to **batch-convert HTML files to Markdown** using `pandoc`, clean up `.html` files, and fix internal links.

#### ⚙️ Requirements

- [pandoc](https://pandoc.org/) installed (`sudo apt install pandoc`)

#### 🚀 Usage

```bash
chmod +x convert-html-to-md.sh
./convert-html-to-md.sh
```

#### 🔧 What It Does

- Converts all `*.html` files (excluding `cdn-cgi/` and `static/`) to `.md`
- Rewrites links like `[example](file.html)` → `[example](file.md)`
- Deletes original `.html` files
- Cleans up backup files created during link rewriting
