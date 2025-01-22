import PyPDF2

def extract_pages(input_pdf_path, output_pdf_path, start_page, end_page):
    # Open the input PDF file
    with open(input_pdf_path, 'rb') as input_pdf:
        reader = PyPDF2.PdfReader(input_pdf)
        writer = PyPDF2.PdfWriter()

        # Iterate through the specified range of pages
        for page_num in range(start_page - 1, end_page): 
            page = reader.pages[page_num]
            writer.add_page(page)

        # Write the extracted pages to the output PDF file
        with open(output_pdf_path, 'wb') as output_pdf:
            writer.write(output_pdf)

input_pdf_path = '/home/codsalah/Downloads/dotss.pdf' 
output_pdf_path = '/home/codsalah/Downloads/exdotss.pdf'  
start_page = 1  # Start page (inclusive)
end_page = 3  # End page (exclusive)

extract_pages(input_pdf_path, output_pdf_path, start_page, end_page)
print(f"Pages {start_page} to {end_page} have been extracted to {output_pdf_path}")