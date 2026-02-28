import PyPDF2
import sys

def extract_text(pdf_path):
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for i in range(len(reader.pages)):
                text += f"\n--- Page {i+1} ---\n"
                text += reader.pages[i].extract_text()
            return text
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    print(extract_text('document.pdf'))
