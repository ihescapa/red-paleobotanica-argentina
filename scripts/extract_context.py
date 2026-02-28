import os
from pypdf import PdfReader

def extract_text_from_pdfs(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            path = os.path.join(directory, filename)
            print(f"Extracting: {filename}")
            try:
                reader = PdfReader(path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                
                output_name = filename.replace(".pdf", ".txt")
                output_path = os.path.join(directory, output_name)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"Saved: {output_name}")
            except Exception as e:
                print(f"Error extracting {filename}: {e}")

if __name__ == "__main__":
    extract_text_from_pdfs("batalla_movimiento/context")
