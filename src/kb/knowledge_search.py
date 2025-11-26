# src/kb/knowledge_search.py
# Simple keyword-based search over loaded KB.
from typing import Dict, Any, Optional
import re
from difflib import SequenceMatcher

def flatten_kb(kb: Dict[str, Any]) -> Dict[str, str]:
    # Produce mapping of keys -> large text for naive search
    out = {}
    for category, items in kb.items():
        if not isinstance(items, dict):
            continue
        for name, content in items.items():
            key = f'{category}/{name}'
            # content may be dict (nested) or simple dict entries
            if isinstance(content, dict):
                text = ''
                for k,v in content.items():
                    text += f' {k} ' + (str(v) if not isinstance(v, dict) else str(v))
            else:
                text = str(content)
            out[key] = re.sub(r'\\s+', ' ', text)
    return out

def find_best_matches(flat: Dict[str, str], query: str, top_k: int = 3):
    q = query.lower()
    scores = []
    for k, text in flat.items():
        t = text.lower()
        # simple presence check
        score = 0
        if q in t:
            score += 100
        # keyword overlap
        for word in q.split():
            if word and word in t:
                score += 10
        # fuzzy ratio
        try:
            ratio = SequenceMatcher(None, q, t[:len(q)+200]).ratio()
            score += int(ratio * 10)
        except Exception:
            pass
        scores.append((score, k, text))
    scores.sort(reverse=True, key=lambda x: x[0])
    return [ {'key': s[1], 'score': s[0], 'snippet': s[2][:800]} for s in scores[:top_k] if s[0]>0 ]

def search_kb(kb: Dict[str, Any], query: str):
    flat = flatten_kb(kb)
    matches = find_best_matches(flat, query, top_k=5)
    return matches
