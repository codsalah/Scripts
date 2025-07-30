#!/usr/bin/env python3
"""
PDF Merger Script
Merges multiple PDF files into a single PDF file.
"""

import PyPDF2
import os
import sys
import glob
from pathlib import Path

def merge_pdfs(pdf_files, output_filename="merged_document.pdf", output_dir=None):
    """
    Merge multiple PDF files into a single PDF.
    
    Args:
        pdf_files (list): List of PDF file paths to merge
        output_filename (str): Name of the output merged PDF file
        output_dir (str): Directory to save the merged PDF (default: same as first input file)
    
    Returns:
        str: Path to the merged PDF file if successful, None otherwise
    """
    if not pdf_files:
        print("❌ Error: No PDF files provided.")
        return None
    
    # Validate all input files exist
    valid_files = []
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file) and pdf_file.lower().endswith('.pdf'):
            valid_files.append(pdf_file)
            print(f"✅ Found: {pdf_file}")
        else:
            print(f"⚠️  Warning: File not found or not a PDF: {pdf_file}")
    
    if not valid_files:
        print("❌ Error: No valid PDF files found.")
        return None
    
    # Determine output directory
    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(valid_files[0]))
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create full output path
    output_path = os.path.join(output_dir, output_filename)
    
    try:
        # Create PDF writer object
        pdf_writer = PyPDF2.PdfWriter()
        
        print(f"\n📄 Merging {len(valid_files)} PDF files...")
        
        # Process each PDF file
        for i, pdf_file in enumerate(valid_files, 1):
            try:
                print(f"📖 Processing file {i}/{len(valid_files)}: {os.path.basename(pdf_file)}")
                
                with open(pdf_file, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    # Add all pages from current PDF
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        pdf_writer.add_page(page)
                    
                    print(f"   ✅ Added {len(pdf_reader.pages)} pages")
                    
            except Exception as e:
                print(f"   ❌ Error processing {pdf_file}: {e}")
                continue
        
        # Write merged PDF to output file
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        total_pages = len(pdf_writer.pages)
        print(f"\n🎉 Success! Merged PDF created:")
        print(f"   📁 Location: {output_path}")
        print(f"   📄 Total pages: {total_pages}")
        print(f"   📊 Files merged: {len(valid_files)}")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error creating merged PDF: {e}")
        return None

def get_pdf_files_from_directory(directory):
    """Get all PDF files from a directory."""
    pdf_pattern = os.path.join(directory, "*.pdf")
    return glob.glob(pdf_pattern)

def main():
    """Main function to handle user input and merge PDFs."""
    print("🔗 PDF Merger Tool")
    print("=" * 30)
    
    # Method 1: Command line arguments
    if len(sys.argv) > 1:
        pdf_files = sys.argv[1:]
        output_name = "merged_document.pdf"
        
        print(f"📝 Command line mode: {len(pdf_files)} files specified")
        
    else:
        # Method 2: Interactive mode
        print("Choose an option:")
        print("1. Enter PDF file paths manually")
        print("2. Merge all PDFs from a directory")
        print("3. Use current directory")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            # Manual file input
            print("\nEnter PDF file paths (one per line, empty line to finish):")
            pdf_files = []
            while True:
                file_path = input("PDF file path: ").strip()
                if not file_path:
                    break
                pdf_files.append(file_path)
                
        elif choice == "2":
            # Directory input
            directory = input("Enter directory path: ").strip()
            if not directory:
                directory = "."
            
            if not os.path.exists(directory):
                print(f"❌ Error: Directory '{directory}' does not exist.")
                return
            
            pdf_files = get_pdf_files_from_directory(directory)
            print(f"📁 Found {len(pdf_files)} PDF files in '{directory}'")
            
        elif choice == "3":
            # Current directory
            pdf_files = get_pdf_files_from_directory(".")
            print(f"📁 Found {len(pdf_files)} PDF files in current directory")
            
        else:
            print("❌ Invalid choice.")
            return
        
        # Get output filename
        output_name = input(f"\nEnter output filename (default: merged_document.pdf): ").strip()
        if not output_name:
            output_name = "merged_document.pdf"
        
        # Ensure .pdf extension
        if not output_name.lower().endswith('.pdf'):
            output_name += '.pdf'
    
    # Merge PDFs
    if pdf_files:
        result = merge_pdfs(pdf_files, output_name)
        if result:
            print(f"\n✨ Merge completed successfully!")
        else:
            print(f"\n💥 Merge failed!")
    else:
        print("❌ No PDF files to merge.")

if __name__ == "__main__":
    main()
