# prompts.py
from loguru import logger

COMMON_PROMPT_START = """You are an expert proofreader and editor, highly skilled in {language_variant} grammar, spelling, and style. Your task is to correct the following {doc_type} document, ensuring it adheres to {language_variant} conventions. Please follow these guidelines:"""

CONTEXT_PROMPT = """
Keep in mind the style, tense, and grammar of the corrected versions of the previous paragraphs to maintain consistency:

{context}

Now, correct the following paragraph while maintaining consistency with the above context:
"""

COMMON_PROMPT_END = """
Original Text:
{text}

Corrected Text:
"""

DOCUMENT_PROMPTS = {
    "Legal": """
1. Correct any grammatical errors and spelling mistakes. Ensure proper punctuation and capitalization.
2. Ensure clarity, coherence, consistency, and correctness throughout the document.
3. Do not add or remove information; focus only on language correction.
4. Maintain the original legal tone and structure of the document.
5. Do not alter any dates, numbers, party names, or legal citations.
6. Ensure proper use of legal jargon and terminology.
7. If the text is already correct, return it unchanged.
8. Ensure that only the corrected text is returned without any additional commentary, explanations, or quotation marks.
""",

"Editorial": """
1. Correct any grammatical errors and spelling mistakes. Ensure proper punctuation and capitalization.
2. Ensure clarity, coherence, consistency, and correctness throughout the document.
3. Do not add or remove information; focus only on language correction.
4. Maintain the original tone and style of the editorial piece.
5. Preserve factual claims, opinions, and assertions as presented in the original content.
6. Maintain the author's original intent and message.
7. If the text is already correct, return it unchanged.
8. Ensure that only the corrected text is returned without any additional commentary, explanations, or quotation marks.
""",

"Medical": """
1. Correct any grammatical errors and spelling mistakes. Ensure proper punctuation and capitalization.
2. Ensure clarity, coherence, consistency, and correctness throughout the document.
3. Do not add or remove information; focus only on language correction.
4. Maintain the original medical tone and terminology.
5. Do not alter any medical terms, drug names, dosages, or patient information.
6. Ensure proper use of medical abbreviations and units of measurement.
7. If the text is already correct, return it unchanged.
8. Ensure that only the corrected text is returned without any additional commentary, explanations, or quotation marks.
""",

"Academic": """
1. Correct any grammatical errors and spelling mistakes. Ensure proper punctuation and capitalization.
2. Ensure clarity, coherence, consistency, and correctness throughout the document.
3. Do not add or remove information; focus only on language correction.
4. Maintain the formal academic tone and structure of the document.
5. Do not alter any technical terms, theories, concepts, equations, or statistical data.
6. Maintain the academic integrity and logical structure of the content.
7. If the text is already correct, return it unchanged.
8. Ensure that only the corrected text is returned without any additional commentary, explanations, or quotation marks.
""",

"Business": """
1. Correct any grammatical errors and spelling mistakes. Ensure proper punctuation and capitalization.
2. Ensure clarity, coherence, consistency, and correctness throughout the document.
3. Do not add or remove information; focus only on language correction.
4. Maintain a professional and clear business tone throughout the document.
5. Do not alter any financial figures, dates, or company-specific information.
6. Ensure proper use of business terminology and acronyms.
7. If the text is already correct, return it unchanged.
8. Ensure that only the corrected text is returned without any additional commentary, explanations, or quotation marks.
""",

"Technical": """
1. Correct any grammatical errors and spelling mistakes. Ensure proper punctuation and capitalization.
2. Ensure clarity, coherence, consistency, and correctness throughout the document.
3. Do not add or remove information; focus only on language correction.
4. Maintain the precise technical tone and terminology of the document.
5. Do not alter any technical terms, codes, specifications, or mathematical equations.
6. Ensure consistency in the use of technical abbreviations and units.
7. If the text is already correct, return it unchanged.
8. Ensure that only the corrected text is returned without any additional commentary, explanations, or quotation marks.
""",

"Creative": """
1. Correct any grammatical errors and spelling mistakes. Ensure proper punctuation and capitalization.
2. Ensure clarity, coherence, consistency, and correctness throughout the document.
3. Do not add or remove information; focus only on language correction.
4. Maintain the original creative style, tone, and voice of the document.
5. Do not alter any intentional literary devices, metaphors, or unconventional elements.
6. Ensure consistency in creative elements (such as character names, settings, plot points, and stylistic choices) and details throughout the document.
7. If the text is already correct, return it unchanged.
8. Ensure that only the corrected text is returned without any additional commentary, explanations, or quotation marks.
""",

"Personal": """
1. Correct any grammatical errors and spelling mistakes. Ensure proper punctuation and capitalization.
2. Ensure clarity, coherence, consistency, and correctness throughout the document.
3. Do not add or remove information; focus only on language correction.
4. Maintain the personal tone and voice of the document.
5. Do not alter any personal information, dates, or specific details provided.
6. Ensure appropriate level of formality based on the document type.
7. If the text is already correct, return it unchanged.
8. Ensure that only the corrected text is returned without any additional commentary, explanations, or quotation marks.
""",

"Marketing": """
1. Correct any grammatical errors and spelling mistakes. Ensure proper punctuation and capitalization.
2. Ensure clarity, coherence, consistency, and correctness throughout the document.
3. Do not add or remove information; focus only on language correction.
4. Maintain the persuasive and engaging tone appropriate for marketing content.
5. Do not alter any product names, slogans, trademarked terms, or campaign-specific data.
6. Ensure consistency in brand voice and messaging throughout the document.
7. If the text is already correct, return it unchanged.
8. Ensure that only the corrected text is returned without any additional commentary, explanations, or quotation marks.
""",

"Financial": """
1. Correct any grammatical errors and spelling mistakes. Ensure proper punctuation and capitalization.
2. Ensure clarity, coherence, consistency, and correctness throughout the document.
3. Do not add or remove information; focus only on language correction.
4. Maintain the precise and formal tone required for financial documents.
5. Do not alter any financial figures, dates, account information, or numerical data.
6. Ensure accuracy and consistency in financial terminology and abbreviations.
7. If the text is already correct, return it unchanged.
8. Ensure that only the corrected text is returned without any additional commentary, explanations, or quotation marks.
""",

"Other": """
1. Correct any grammatical errors and spelling mistakes. Ensure proper punctuation and capitalization.
2. Ensure clarity, coherence, consistency, and correctness throughout the document.
3. Do not add or remove information; focus only on language correction.
4. Maintain the original tone and structure of the document.
5. Do not alter any factual information, key details, or specific terminology.
6. Ensure proper formatting appropriate to the document type.
7. If the text is already correct, return it unchanged.
8. Ensure that only the corrected text is returned without any additional commentary, explanations, or quotation marks.
"""
}

def get_doc_prompt(doc_type, context, text, language_variant, custom_prompt=None):
    """
    Retrieves and formats the prompt for a given document type.

    :param doc_type: The type of the document.
    :param context: The context (corrected versions of previous paragraphs) as a string.
    :param text: The original text of the document.
    :param language_variant: The language variant (e.g., "British English").
    :param custom_prompt: Optional custom prompt to use instead of predefined prompts.
    :return: Formatted prompt string.
    """
    if custom_prompt:
        specific_prompt = custom_prompt
    else:
        specific_prompt = DOCUMENT_PROMPTS.get(doc_type, DOCUMENT_PROMPTS["Other"])
    
    prompt_parts = [
        COMMON_PROMPT_START,
        specific_prompt,
        CONTEXT_PROMPT if context else "",
        COMMON_PROMPT_END
    ]
    
    full_prompt = "\n\n".join(filter(bool, prompt_parts))
    
    full_prompt = full_prompt.format(
        doc_type=doc_type,
        language_variant=language_variant,
        context=context,
        text=text
    )
    
    # Add logging for a sanity check
    logger.info(f"Generating prompt for document type: {doc_type}")
    logger.info(f"Language variant: {language_variant}")
    logger.info(f"Context provided: {'Yes' if context else 'No'}")
    logger.info(f"Custom prompt provided: {'Yes' if custom_prompt else 'No'}")
    logger.info(f"Text length: {len(text)} characters")
    logger.info(f"Generated prompt length: {len(full_prompt)} characters")
    logger.info(f"Generated prompt: {full_prompt}")
    return full_prompt