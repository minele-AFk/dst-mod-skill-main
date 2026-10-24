import PyPDF2
import sys

def read_pdf_to_txt(pdf_path, output_path=None):
    reader = PyPDF2.PdfReader(pdf_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text() + '\n'
    
    if output_path is None:
        output_path = pdf_path.replace('.pdf', '_content.txt')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(f'Done! Content saved to: {output_path}')
    return text

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python read_pdf.py <pdf_path> [output_path]')
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    read_pdf_to_txt(pdf_path, output_path)