import fitz  # PyMuPDF
import sys
from pathlib import Path

# Usage
"""
python "Change pdf background color/Change_BG_color_PDFs.py" 
"/path/to/pdf" 
"#FAF9F6" //off-white bg color
""" 

def hex_to_rgb_normalized(hex_color: str):
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError("Hex color must be 6 digits like #AABBCC")
    return tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))


# ---- runtime input ----
if len(sys.argv) < 3:
    print("Usage: python script.py input.pdf #RRGGBB")
    sys.exit(1)

input_path = Path(sys.argv[1])
hex_color = sys.argv[2]

background_color = hex_to_rgb_normalized(hex_color)

# ---- auto output name ----
output_path = input_path.with_name(input_path.stem + "_bg" + input_path.suffix)

# ---- processing ----
with fitz.open(input_path) as doc:
    for page in doc:
        page.draw_rect(page.rect, color=None, fill=background_color, overlay=False)

    doc.save(output_path)

print(f"Saved to: {output_path}")