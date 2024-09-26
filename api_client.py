# api_client.py

import asyncio
import aiohttp
from cache_manager import get_from_cache, save_to_cache
from utils import count_tokens
from loguru import logger
from aiolimiter import AsyncLimiter

class GrammarCorrectorAPI:
    def __init__(self, api_key, language_variant, model="gpt-4o-mini", rate_limit=450, rate_period=60):
        self.api_key = api_key
        self.language_variant = language_variant
        self.model = model
        self.rate_limiter = AsyncLimiter(rate_limit, rate_period)
        self.max_retries = 5
        self.backoff_factor = 2

    async def correct_paragraphs(self, paragraphs, total_token_limit, progress_callback, prompt_template):
        """
        Corrects multiple paragraphs using a provided prompt template.

        :param paragraphs: List of paragraph texts to correct.
        :param total_token_limit: Maximum total tokens allowed for processing.
        :param progress_callback: Callback function to update progress.
        :param prompt_template: Template string for the prompt with placeholders.
        :return: Tuple of (corrected_paragraphs, unprocessed_paragraphs)
        """
        corrected = []
        unprocessed = []
        async with aiohttp.ClientSession() as session:
            tokens_processed = 0
            for para in paragraphs:
                tokens = count_tokens(para, self.model)
                if tokens_processed + tokens > total_token_limit:
                    unprocessed.append(para)
                    continue

                # Format the prompt with the current paragraph and language variant
                prompt = prompt_template.format(text=para, language_variant=self.language_variant)

                corrected_text, tokens_corrected = await self.correct_text(session, para, tokens_processed, prompt)
                corrected.append(corrected_text)
                tokens_processed += tokens_corrected

                if progress_callback:
                    progress_callback(tokens_corrected)
        return corrected, unprocessed

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
                    "temperature": 0.3,
                    "max_tokens": 1000,  # Adjust as needed
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
