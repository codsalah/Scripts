import fitz  # PyMuPDF

# Example usage
input_pdf_path = "/home/codsalah/Documents/DDIA1.pdf"  
output_pdf_path = "/home/codsalah/Documents/DDIA5.pdf"

background_color = (200 / 255, 210 / 255, 180 / 255)  # Define background color once
with fitz.open(input_pdf_path) as doc:
    for page in doc:
        # Apply background fill in one step instead of drawing a rectangle
        page.draw_rect(page.rect, color=None, fill=background_color, overlay=False)

    doc.save(output_pdf_path)

print("Background color changed and saved to", output_pdf_path)
