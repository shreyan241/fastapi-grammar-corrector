# cache_manager.py

import json
import os
from loguru import logger

CACHE_FILE = "correction_cache.json"

def get_from_cache(key):
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        return cache.get(key)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def save_to_cache(key, value):
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
        else:
            cache = {}
    except (json.JSONDecodeError):
        cache = {}
    
    cache[key] = value
    
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=4)

def clear_cache():
    try:
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
            logger.info(f"Cache file {CACHE_FILE} deleted successfully.")
    except Exception as e:
        logger.error(f"Failed to delete cache file {CACHE_FILE}: {e}")
