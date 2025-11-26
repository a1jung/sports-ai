# src/kb/knowledge_loader.py
# Load local JSON knowledge files into a dict for fast lookup.
import os
import json
from typing import Dict, Any

DATA_DIR = os.path.abspath('data')

def load_all_knowledge() -> Dict[str, Dict[str, Any]]:
    result = {}
    if not os.path.exists(DATA_DIR):
        return result

    for category in os.listdir(DATA_DIR):
        cat_path = os.path.join(DATA_DIR, category)
        if os.path.isdir(cat_path):
            result[category] = {}
            # files in this category (either direct json files or subfolders)
            for entry in os.listdir(cat_path):
                entry_path = os.path.join(cat_path, entry)
                if os.path.isfile(entry_path) and entry_path.endswith('.json'):
                    name = os.path.splitext(entry)[0]
                    try:
                        with open(entry_path, 'r', encoding='utf-8') as f:
                            result[category][name] = json.load(f)
                    except Exception:
                        result[category][name] = None
                elif os.path.isdir(entry_path):
                    # nested folder (e.g., yacht/470) - try load description.json and other jsons
                    result[category][entry] = {}
                    for sub in os.listdir(entry_path):
                        sub_path = os.path.join(entry_path, sub)
                        if os.path.isfile(sub_path) and sub_path.endswith('.json'):
                            subname = os.path.splitext(sub)[0]
                            try:
                                with open(sub_path, 'r', encoding='utf-8') as f:
                                    result[category][entry][subname] = json.load(f)
                            except Exception:
                                result[category][entry][subname] = None
    return result
