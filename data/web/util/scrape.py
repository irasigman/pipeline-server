import os

import requests

def reader_page(url):
    JINA_KEY = os.getenv("JINA_KEY")
    if not JINA_KEY:
        raise ValueError("JINA_KEY environment variable not set")

    headers = {
        'Authorization': f'Bearer {JINA_KEY}',
        'X-Respond-With': "readerlm-v2"
    }
    response = requests.get(f'https://r.jina.ai/{url}', headers=headers)
    print(response.text)

    return response.text
