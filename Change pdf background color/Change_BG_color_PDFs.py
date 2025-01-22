import fitz  # PyMuPDF

# Example usage
input_pdf_path = "/home/codsalah/Downloads/Logic - Logical Fallacies.pdf"  
output_pdf_path = "/home/codsalah/Downloads/Logic - Logical Fallacies2.pdf" 

background_color = (200/255, 210/255, 180/255) 
doc = fitz.open(input_pdf_path)
for page in doc:
    page.draw_rect(page.rect, color=None, fill=background_color, overlay=False)

doc.ez_save(output_pdf_path)
doc.close()
print("Background color changed and saved to", output_pdf_path)

