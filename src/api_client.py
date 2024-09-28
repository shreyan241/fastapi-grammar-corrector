# api_client.py

import asyncio
import aiohttp
from src.cache_manager import get_from_cache, save_to_cache
from src.utils import count_tokens
from src.prompts import get_doc_prompt
from src.config import (DEFAULT_CONTEXT_WINDOW_SIZE, DEFAULT_TEMPERATURE, DEFAULT_BACKOFF_FACTOR,
                    DEFAULT_MAX_RETRIES, DEFAULT_RATE_LIMIT, DEFAULT_MODEL,DEFAULT_RATE_PERIOD,
                    DEFAULT_LANGUAGE_VARIANT)
from loguru import logger
from aiolimiter import AsyncLimiter

class GrammarCorrectorAPI:
    def __init__(self, api_key, language_variant=DEFAULT_LANGUAGE_VARIANT, model=DEFAULT_MODEL, rate_limit=DEFAULT_RATE_LIMIT, rate_period=DEFAULT_RATE_PERIOD, temperature=DEFAULT_TEMPERATURE):
        self.api_key = api_key
        self.language_variant = language_variant
        self.model = model
        self.rate_limiter = AsyncLimiter(rate_limit, rate_period)
        self.max_retries = DEFAULT_MAX_RETRIES
        self.backoff_factor = DEFAULT_BACKOFF_FACTOR
        self.temperature = temperature

    async def correct_paragraphs(self, all_paragraphs, selected_indices, total_token_limit, progress_callback, doc_type, language_variant, custom_prompt, context_window_size=DEFAULT_CONTEXT_WINDOW_SIZE):
        """
        Corrects selected paragraphs using the provided document type and language variant.

        :param all_paragraphs: List of all paragraph texts.
        :param selected_indices: List of indices of paragraphs to correct.
        :param total_token_limit: Maximum total tokens allowed for processing.
        :param progress_callback: Callback function to update progress.
        :param doc_type: The type of document being corrected.
        :param language_variant: The language variant to use for correction.
        :param custom_prompt: Custom prompt to use for correction, if provided.
        :param context_window_size: Number of previous paragraphs to use as context.
        :return: Tuple of (corrected_paragraphs, unprocessed_paragraphs)
        """
        corrected = all_paragraphs.copy()
        unprocessed = []
        async with aiohttp.ClientSession() as session:
            tokens_processed = 0
            for i in selected_indices:
                para = all_paragraphs[i]
                tokens = count_tokens(para, self.model)
                if tokens_processed + tokens > total_token_limit:
                    unprocessed.append(para)
                    logger.warning(f"Paragraph {i} exceeds token limit. Skipping.")
                    continue
                
                # get context
                logger.info(f"Processing paragraph {i}")
                context = self.get_context(corrected, i, context_window_size)
                
                # Generate the prompt using get_doc_prompt function
                prompt = get_doc_prompt(doc_type, context, para, language_variant, custom_prompt)

                corrected_text, tokens_corrected = await self.correct_text(session, para, tokens_processed, prompt)
                corrected[i] = (corrected_text)
                tokens_processed += tokens_corrected

                if progress_callback:
                    progress_callback(tokens_corrected)
                logger.info(f"Finished processing paragraph {i}. Tokens corrected: {tokens_corrected}")
                
        return corrected, unprocessed

    def get_context(self, corrected_paragraphs, current_index, context_window_size):
        """
        Get the context for the current paragraph.
        """
        start = max(0, current_index - context_window_size)
        context_paragraphs = []
        # Use corrected text if available, otherwise use original
        for i in range(start, current_index):
            context_paragraphs.append(corrected_paragraphs[i])
            
        context = "\n\n".join(context_paragraphs)
        logger.debug(f"Getting context for paragraph {current_index}. Context size: {len(context_paragraphs)}")
        return context
    
    async def correct_text(self, session, text, tokens_processed, prompt, retry_count=0):
        """
        Corrects a single paragraph using a custom prompt.

        :param session: aiohttp ClientSession.
        :param text: Paragraph text to correct.
        :param tokens_processed: Tokens processed so far.
        :param prompt: Custom prompt for the text.
        :param retry_count: Current retry attempt.
        :return: Tuple of (corrected_text, tokens_corrected)
        """
        # Check cache
        cache_key = f"{text}_{self.language_variant}"
        cached_result = get_from_cache(cache_key)
        if cached_result:
            logger.info(f"Cache hit for paragraph.")
            return cached_result, count_tokens(cached_result, self.model)

        try:
            async with self.rate_limiter:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self.model,  # Use selected model
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": self.temperature,
                    "max_tokens": 4096 if "gpt-3.5" in self.model else 8192,  # Adjust as needed
                    "top_p": 1,
                    "frequency_penalty": 0,
                    "presence_penalty": 0
                }
                async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload) as response:
                    if response.status == 429:
                        if retry_count < self.max_retries:
                            wait_time = self.backoff_factor ** retry_count
                            logger.warning(f"Rate limit hit. Retrying in {wait_time} seconds...")
                            await asyncio.sleep(wait_time)
                            return await self.correct_text(session, text, tokens_processed, prompt, retry_count + 1)
                        else:
                            logger.error("Max retries exceeded. Returning original text.")
                            return text, count_tokens(text, self.model)
                    elif response.status != 200:
                        result = await response.json()
                        error_message = result.get("error", {}).get("message", "Unknown error.")
                        logger.error(f"API Error: {error_message}")
                        return text, count_tokens(text, self.model)

                    result = await response.json()
                    corrected_text = result['choices'][0]['message']['content'].strip()

        except Exception as e:
            logger.error(f"An error occurred during text correction: {e}")
            return text, count_tokens(text, self.model)  # Return original text on error

        # Save to cache
        save_to_cache(cache_key, corrected_text)
        logger.info("Paragraph corrected successfully.")
        return corrected_text, count_tokens(corrected_text, self.model)
