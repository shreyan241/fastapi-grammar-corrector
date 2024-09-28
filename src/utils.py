import tiktoken
from loguru import logger

def count_tokens(text, model="gpt-4o-mini"):
    """
    Counts the number of tokens in the given text using the specified model's encoding.

    Parameters:
        text (str): The text to be tokenized.
        model (str): The model name to determine the encoding. Defaults to "gpt-4o-mini".

    Returns:
        int: The number of tokens in the text.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        logger.info(f"Successfully loaded encoding for model: {model}")
    except KeyError:
        fallback_model = "gpt-3.5-turbo"
        encoding = tiktoken.get_encoding(fallback_model)
        logger.warning(f"Model '{model}' not found. Falling back to encoding for model: {fallback_model}")
    
    tokens = encoding.encode(text)
    token_count = len(tokens)
    logger.debug(f"Text tokenized into {token_count} tokens.")
    return token_count
