# Tetris in a PDF

Abusing PDF field objects to render a monochrome grid, combined with keystroke-entry in a text field to receive inputs.

More info here: https://th0mas.nl/2025/01/12/tetris-in-a-pdf/

This now works in:
- PDFium (Chromium-based browsers); 
- PDF.js (Firefox); 
- FoxIt Reader and Editor; 
- Tracker Software "PDF XChange Editor". 

Not tested for / intended to function in other engines (but you might be able modify this to work in Acrobat I guess).

Generated PDF should validate cleanly using tools such as:
- `qpdf --check tris.pdf`
- `pdfcpu validate tris.pdf`
- `mutool clean -c tris.pdf` (this will create `out.pdf` hence why the Python script now outputs `tris.pdf`!)

