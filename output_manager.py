# output_manager.py

from docx import Document
from fpdf import FPDF
from loguru import logger

def save_corrected_document(input_path, output_path, corrected_text):
    extension = output_path.split('.')[-1].lower()
    if extension == 'docx':
        save_as_docx(output_path, corrected_text)
    elif extension == 'pdf':
        save_as_pdf(output_path, corrected_text)
    elif extension == 'txt':
        save_as_txt(output_path, corrected_text)
    else:
        raise ValueError("Unsupported output file format.")

def save_as_docx(output_path, corrected_text):
    doc = Document()
    paragraphs = corrected_text.split('\n\n')  # Assuming paragraphs are separated by double newlines
    for para in paragraphs:
        doc.add_paragraph(para)
    doc.save(output_path)
    logger.info(f"Saved corrected document as DOCX: {output_path}")

def save_as_pdf(output_path, corrected_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    
    paragraphs = corrected_text.split('\n\n')
    for para in paragraphs:
        pdf.multi_cell(0, 10, para)
        pdf.ln()
    
    pdf.output(output_path)
    logger.info(f"Saved corrected document as PDF: {output_path}")

def save_as_txt(output_path, corrected_text):
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(corrected_text)
    logger.info(f"Saved corrected document as TXT: {output_path}")
