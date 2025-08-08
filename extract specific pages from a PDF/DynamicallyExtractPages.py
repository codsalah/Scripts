#!/usr/bin/env python3
"""
Split a single PDF into multiple sub-PDFs given page ranges.

Usage (CLI):
    python split_pdf_ranges.py input.pdf "1:3 3:9 9:11" /path/to/output_dir

If output_dir is omitted it writes files next to input PDF.

Interactive mode:
    Run without args and follow prompts.
"""

import os
import sys
import argparse
from typing import List, Tuple
import PyPDF2

def parse_ranges(ranges_str: str) -> List[Tuple[int, int]]:
    """
    Parse a ranges string like "1:3 3:9 9:11" or "1-3,3-9,9-11" into list of (start,end).
    Accepts separators ':' or '-'. Ranges separated by whitespace or commas.
    """
    ranges = []
    if not ranges_str:
        return ranges
    for part in ranges_str.replace(',', ' ').split():
        if ':' in part:
            sep = ':'
        elif '-' in part:
            sep = '-'
        else:
            raise ValueError(f"Invalid range '{part}'. Use start:end or start-end.")
        s, e = part.split(sep, 1)
        try:
            start = int(s.strip())
            end = int(e.strip())
        except ValueError:
            raise ValueError(f"Invalid integers in range '{part}'.")
        ranges.append((start, end))
    return ranges

def extract_range(reader: PyPDF2.PdfReader, start: int, end: int, output_path: str) -> bool:
    """
    Extract pages start..end inclusive (1-based) from reader and write to output_path.
    Returns True on success, False on failure.
    """
    try:
        total_pages = len(reader.pages)
        if start < 1:
            print(f"Error: start page {start} must be >= 1.")
            return False
        if start > total_pages:
            print(f"Error: start page {start} exceeds total pages ({total_pages}). Skipping.")
            return False
        if end > total_pages:
            print(f"Warning: end page {end} exceeds total pages ({total_pages}). Using {total_pages}.")
            end = total_pages
        if start > end:
            print(f"Error: start page {start} > end page {end}. Skipping.")
            return False

        writer = PyPDF2.PdfWriter()
        for p in range(start - 1, end):
            try:
                writer.add_page(reader.pages[p])
            except Exception as exc:
                print(f"Warning: failed to add page {p+1}: {exc}")

        # Ensure output directory exists
        out_dir = os.path.dirname(output_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        with open(output_path, 'wb') as out_f:
            writer.write(out_f)

        print(f"Saved pages {start}-{end} to: {output_path}")
        return True

    except Exception as exc:
        print(f"Unexpected error extracting {start}-{end}: {exc}")
        return False

def split_pdf_by_ranges(input_pdf_path: str, ranges: List[Tuple[int,int]], output_dir: str = None) -> None:
    if not os.path.exists(input_pdf_path):
        print(f"Error: input file does not exist: {input_pdf_path}")
        return

    base_name = os.path.splitext(os.path.basename(input_pdf_path))[0]
    if output_dir is None or output_dir.strip() == "":
        output_dir = os.path.dirname(input_pdf_path)
    if not output_dir:
        output_dir = os.getcwd()
    os.makedirs(output_dir, exist_ok=True)

    try:
        with open(input_pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            total_pages = len(reader.pages)
            print(f"Input PDF: {input_pdf_path}  (total pages: {total_pages})")

            for idx, (start, end) in enumerate(ranges, start=1):
                out_name = f"{base_name}_part{idx}_{start}-{end}.pdf"
                out_path = os.path.join(output_dir, out_name)
                extract_range(reader, start, end, out_path)

    except PyPDF2.errors.DependencyError as e:
        print("Dependency Error:", e)
        print("If asked, run: pip install pycryptodome")
    except PyPDF2.errors.PdfReadError as e:
        print("PDF Read Error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)

def main():
    parser = argparse.ArgumentParser(description="Extract multiple sub-PDFs from a single PDF by ranges.")
    parser.add_argument('input_pdf', nargs='?', help='Path to input PDF')
    parser.add_argument('ranges', nargs='?', help='Ranges string e.g. "1:3 3:9 9:11" (quotes recommended)')
    parser.add_argument('output_dir', nargs='?', help='Output directory (optional)')
    args = parser.parse_args()

    if args.input_pdf and args.ranges:
        try:
            ranges = parse_ranges(args.ranges)
        except ValueError as e:
            print(f"Error parsing ranges: {e}")
            return
        split_pdf_by_ranges(args.input_pdf, ranges, args.output_dir)
        return

    # Interactive fallback
    print("PDF Multi-Range Extractor")
    print("=========================")
    input_pdf = input("Enter input PDF path: ").strip()
    if not input_pdf:
        print("No input provided. Exiting.")
        return

    ranges_str = input("Enter ranges (e.g. 1:3 3:9 9:11): ").strip()
    if not ranges_str:
        print("No ranges provided. Exiting.")
        return

    out_dir = input("Enter output directory (press Enter to use input file's directory): ").strip() or None

    try:
        ranges = parse_ranges(ranges_str)
    except ValueError as e:
        print(f"Error parsing ranges: {e}")
        return

    split_pdf_by_ranges(input_pdf, ranges, out_dir)

if __name__ == "__main__":
    main()
