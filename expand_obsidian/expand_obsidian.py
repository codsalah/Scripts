import os
import re
from datetime import datetime

# Configuration
SOURCE_DIR = './' 
OUTPUT_DIR = './expanded_notes'
METADATA_TEMPLATE = """Up: [[{parent_name}]]
Tags: #literature #docker
Topics:
prerequisites:
Teacher/Author:
Link:
A-N-K-I:
date: {date}
time: {time}

---

# 🧠 {note_title}

---

{content}
"""

def refactor_obsidian_vault():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Pattern to find: ## [[Title]] followed by content until next ## or separator
    section_pattern = re.compile(r'## \[\[(.*?)\]\]\n(.*?)(?=\n## \[\[|\n---|\Z)', re.DOTALL)
    
    files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.md') and f != "README.md"]

    for filename in files:
        parent_name = filename.replace('.md', '')
        file_path = os.path.join(SOURCE_DIR, filename)

        with open(file_path, 'r', encoding='utf-8') as f:
            full_text = f.read()

        # 1. Identify sections to move
        sections = section_pattern.findall(full_text)
        
        if not sections:
            continue

        print(f"Refactoring {filename}...")
        
        # 2. Extract the parent's header/frontmatter (everything before the first ## [[)
        # We keep this to preserve the parent's original metadata
        parent_header = full_text.split('## [[')[0].strip()
        
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")

        # 3. Create the sub-notes and build the new parent reference list
        reference_list = ["\n### Sub-Topics"]
        
        for title, body in sections:
            # Create sub-note file
            new_filename = f"{title}.md"
            new_file_path = os.path.join(OUTPUT_DIR, new_filename)
            
            sub_content = METADATA_TEMPLATE.format(
                parent_name=parent_name,
                note_title=title,
                content=body.strip(),
                date=current_date,
                time=current_time
            )

            with open(new_file_path, 'w', encoding='utf-8') as nf:
                nf.write(sub_content)
            
            # Add to the parent's new reference list
            reference_list.append(f"    * [[{title}]]")

        # 4. Rewrite the Parent File
        # It will now contain the original top metadata + the clean list of sub-links
        new_parent_content = parent_header + "\n" + "\n".join(reference_list)
        
        # Saving parent to OUTPUT_DIR to avoid overwriting original until you're happy
        with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as pf:
            pf.write(new_parent_content)

        print(f"  -> Done: Created {len(sections)} sub-notes and cleaned parent.")

if __name__ == "__main__":
    refactor_obsidian_vault()