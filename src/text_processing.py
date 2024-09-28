# text_processing.py

import re

def split_into_paragraphs(text):
    paragraphs = re.split(r'\n{2,}', text)
    # Remove any leading/trailing whitespace
    paragraphs = [para.strip() for para in paragraphs if para.strip()]
    return paragraphs

def split_paragraph_into_sentences(paragraph):
    # Simple sentence splitter using regex
    sentences = re.split(r'(?<=[.!?]) +', paragraph)
    # Remove any leading/trailing whitespace
    sentences = [sent.strip() for sent in sentences if sent.strip()]
    return sentences
