# src/ai/web_search.py
# Optional: use Bing Web Search API (requires BING_API_KEY env var)
import os
import httpx

BING_KEY = os.getenv('BING_API_KEY')

def bing_search(query: str, count: int = 3):
    if not BING_KEY:
        return None
    endpoint = 'https://api.bing.microsoft.com/v7.0/search'
    headers = {'Ocp-Apim-Subscription-Key': BING_KEY}
    params = {'q': query, 'count': count, 'mkt': 'en-US'}
    try:
        r = httpx.get(endpoint, headers=headers, params=params, timeout=10.0)
        r.raise_for_status()
        data = r.json()
        results = []
        web_pages = data.get('webPages', {}).get('value', [])
        for item in web_pages:
            results.append({'name': item.get('name'), 'snippet': item.get('snippet'), 'url': item.get('url')})
        return results
    except Exception as e:
        return None
