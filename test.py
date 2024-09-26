# sample_split.py

import re
from docx import Document

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

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def main():
    file_path = 'sample.docx'  # Replace with your sample Word file path
    text = extract_text_from_docx(file_path)
    paragraphs = split_into_paragraphs(text)
    
    print("Extracted Paragraphs:")
    for idx, para in enumerate(paragraphs, 1):
        print(f"\nParagraph {idx}:\n{para}")
        
        # Optionally, split into sentences and print them
        sentences = split_paragraph_into_sentences(para)
        print("Sentences:")
        for s_idx, sentence in enumerate(sentences, 1):
            print(f"  {s_idx}. {sentence}")

if __name__ == "__main__":
    main()
