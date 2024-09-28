# output_manager.py

import os
from docx import Document
from fpdf import FPDF
from loguru import logger

def save_corrected_document(input_path, output_path, corrected_text):
    try:
        extension = output_path.split('.')[-1].lower()
        if extension == 'docx':
            save_as_docx(output_path, corrected_text)
        elif extension == 'pdf':
            save_as_pdf(output_path, corrected_text)
        elif extension == 'txt':
            save_as_txt(output_path, corrected_text)
        else:
            raise ValueError(f"Unsupported output file format: {extension}")
        logger.info(f"Successfully saved corrected document: {output_path}")
    except Exception as e:
        logger.error(f"Error saving corrected document: {str(e)}")
        raise

def save_as_docx(output_path, corrected_text):
    try:
        doc = Document()
        paragraphs = corrected_text.split('\n\n')  # Assuming paragraphs are separated by double newlines
        for para in paragraphs:
            doc.add_paragraph(para)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc.save(output_path)
        logger.info(f"Saved corrected document as DOCX: {output_path}")
    except Exception as e:
        logger.error(f"Error saving DOCX: {str(e)}")
        raise

def save_as_pdf(output_path, corrected_text):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        
        paragraphs = corrected_text.split('\n\n')
        for para in paragraphs:
            # Encode to handle non-ASCII characters
            encoded_para = para.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 10, encoded_para)
            pdf.ln()
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf.output(output_path)
        logger.info(f"Saved corrected document as PDF: {output_path}")
    except Exception as e:
        logger.error(f"Error saving PDF: {str(e)}")
        raise

def save_as_txt(output_path, corrected_text):
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(corrected_text)
        logger.info(f"Saved corrected document as TXT: {output_path}")
    except Exception as e:
        logger.error(f"Error saving TXT: {str(e)}")
        raise