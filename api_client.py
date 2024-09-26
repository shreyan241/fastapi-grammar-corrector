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
    
    async def correct_paragraphs(self, paragraphs, total_token_limit, progress_callback):
        corrected = []
        unprocessed = []
        async with aiohttp.ClientSession() as session:
            tokens_processed = 0
            for para in paragraphs:
                tokens = count_tokens(para, self.model)
                if tokens_processed + tokens > total_token_limit:
                    unprocessed.append(para)
                    continue
                corrected_text, tokens = await self.correct_text(session, para, tokens_processed)
                corrected.append(corrected_text)
                tokens_processed += tokens
                if progress_callback:
                    progress_callback(tokens)
        return corrected, unprocessed

    
    async def correct_text(self, session, text, tokens_processed, retry_count=0):
        # Check cache
        cache_key = f"{text}_{self.language_variant}"
        cached_result = get_from_cache(cache_key)
        if cached_result:
            logger.info(f"Cache hit for paragraph.")
            return cached_result, count_tokens(cached_result, self.model)
    
        # Prepare the prompt
        prompt = f"""You are an expert proofreader and editor, highly skilled in {self.language_variant} grammar, spelling, and style. Your task is to correct the following text, ensuring it adheres to {self.language_variant} conventions. Please follow these guidelines:
    
1. Correct any grammatical errors and spelling mistakes.
2. Maintain the original tone and style of the text.
3. Ensure clarity, coherence, consistency, and correctness throughout the text.
4. Ensure proper punctuation and capitalization.
5. Do not add or remove information; focus only on language correction.
6. If the text is already correct, simply return it unchanged.
7. Ensure that only the corrected text is returned without any additional commentary, explanations, or quotation marks.
    
Original Text:
{text}
    
Corrected Text:
"""
    
        try:
            async with self.rate_limiter:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self.model,  # Use selected model
                    "messages": [
                        {"role": "system", "content": f"You are a helpful assistant specialized in {self.language_variant} grammar and spelling correction."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000,  # Adjust as needed
                    "n": 1,
                }
                async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload) as response:
                    if response.status == 429:
                        if retry_count < self.max_retries:
                            wait_time = self.backoff_factor ** retry_count
                            logger.warning(f"Rate limit hit. Retrying in {wait_time} seconds...")
                            await asyncio.sleep(wait_time)
                            return await self.correct_text(session, text, tokens_processed, retry_count + 1)
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
