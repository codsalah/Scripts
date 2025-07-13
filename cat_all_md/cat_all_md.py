import os
import re
import sys

def extract_note_references(content):
    pattern = r'\[\[([^\]]+)\]\]'
    matches = re.findall(pattern, content)
    return matches

def find_markdown_file(note_name, search_path):
    for root, dirs, files in os.walk(search_path):
        # Try exact match first
        exact_match = note_name + ".md"
        if exact_match in files:
            return os.path.join(root, exact_match)

        # Try case-insensitive match
        for file in files:
            if file.lower() == exact_match.lower():
                return os.path.join(root, file)

    return None

def read_parent_file(parent_file_path):
    try:
        with open(parent_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Skip the first 10 lines (metadata) and join the rest
        if len(lines) > 10:
            content = ''.join(lines[10:])
        else:
            content = ''

        return extract_note_references(content)
    except FileNotFoundError:
        print(f"ERROR: Parent file not found: {parent_file_path}")
        return []
    except Exception as e:
        print(f"ERROR reading parent file: {e}")
        return []

def get_note_references_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Skip the first 10 lines and join the rest
        if len(lines) > 10:
            content = ''.join(lines[10:])
        else:
            content = ''

        return extract_note_references(content)
    except Exception as e:
        print(f"ERROR reading file {file_path}: {e}")
        return []

def collect_all_references_recursive(initial_references, search_folder, max_depth=3, processed_files=None, current_depth=0):
    if processed_files is None:
        processed_files = set()

    all_files = []

    for note_name in initial_references:
        # Skip if already processed to avoid duplicates
        if note_name in processed_files:
            print(f"Level {current_depth + 1}: Skipping duplicate {note_name}")
            continue

        file_path = find_markdown_file(note_name, search_folder)
        if file_path:
            all_files.append((note_name, file_path))
            processed_files.add(note_name)
            print(f"Level {current_depth + 1}: Found {note_name} -> {file_path}")

            # Recursively process references from this file (depth-first)
            if current_depth < max_depth - 1:  # Don't process references at max depth
                nested_refs = get_note_references_from_file(file_path)
                if nested_refs:
                    print(f"Level {current_depth + 1}: {note_name} has {len(nested_refs)} nested references: {nested_refs}")
                    # Recursively collect nested references (depth-first)
                    nested_files = collect_all_references_recursive(
                        nested_refs, search_folder, max_depth, processed_files, current_depth + 1
                    )
                    all_files.extend(nested_files)
        else:
            print(f"Level {current_depth + 1}: Missing {note_name}")

    return all_files

def concatenate_notes(parent_file_path, search_folder, output_file, max_depth=3):
    print(f"Reading parent file: {parent_file_path}")
    initial_references = read_parent_file(parent_file_path)

    if not initial_references:
        print("ERROR: No note references found in parent file.")
        return

    print(f"Found {len(initial_references)} initial note references: {initial_references}")
    print(f"Starting recursive collection with max depth: {max_depth}")

    # Collect all references recursively (depth-first)
    all_files = collect_all_references_recursive(initial_references, search_folder, max_depth)

    if not all_files:
        print("ERROR: No files found to process.")
        return

    print(f"\nTotal unique files collected: {len(all_files)}")

    # Write concatenated content
    print(f"\nWriting to: {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for note_name, file_path in all_files:
                print(f"Processing: {note_name}")
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        lines = infile.readlines()

                        # Skip the first 10 lines and get the rest of the content
                        if len(lines) > 10:
                            content_lines = lines[10:]
                        else:
                            content_lines = []

                        # Remove trailing empty lines
                        while content_lines and content_lines[-1].strip() == '':
                            content_lines.pop()

                        content = ''.join(content_lines)

                        outfile.write(f"# {note_name}\n\n")
                        outfile.write(content)
                        outfile.write("\n\n---\n\n")
                except Exception as e:
                    print(f"ERROR reading {file_path}: {e}")

        print(f"Successfully created: {output_file}")
        print(f"Processed {len(all_files)} unique files")

    except Exception as e:
        print(f"ERROR writing output file: {e}")

# Configuration
SEARCH_FOLDER = "/home/codsalah/Documents/salah-space/3. Notes/"
PARENT_FILE = os.path.join(SEARCH_FOLDER, "SQL ITI Database (RAMI).md") 
OUTPUT_FILE = os.path.join(SEARCH_FOLDER, "CombinedITISQLNotes__.md")

if __name__ == "__main__":
    # Allow command line arguments for flexibility
    if len(sys.argv) >= 2:
        PARENT_FILE = sys.argv[1]
    if len(sys.argv) >= 3:
        OUTPUT_FILE = sys.argv[2]
    if len(sys.argv) >= 4:
        SEARCH_FOLDER = sys.argv[3]

    print("Dynamic Markdown Concatenator (Recursive)")
    print(f"Search folder: {SEARCH_FOLDER}")
    print(f"Parent file: {PARENT_FILE}")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Max recursion depth: 3")
    print("-" * 50)

    concatenate_notes(PARENT_FILE, SEARCH_FOLDER, OUTPUT_FILE, max_depth=3)
