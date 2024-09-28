# file_handlers.py

from docx import Document
import pdfplumber

def extract_text(file_path):
    extension = file_path.split('.')[-1].lower()
    if extension == 'docx':
        return extract_text_from_docx(file_path)
    elif extension == 'pdf':
        return extract_text_from_pdf(file_path)
    elif extension == 'txt':
        return extract_text_from_txt(file_path)
    else:
        raise ValueError("Unsupported file format.")

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def extract_text_from_pdf(file_path):
    full_text = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
    return '\n'.join(full_text)

def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
