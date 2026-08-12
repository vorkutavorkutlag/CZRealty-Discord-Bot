import requests
import json
import os
from bs4 import BeautifulSoup

BASE_URL   = "https://www.sreality.cz"
SEARCH_URL = "https://www.sreality.cz/en/search/apartments/praha"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ESTATE_CACHE_PATH = os.path.join(BASE_DIR, "estate_cache.json")


def load_cache() -> dict:
    try:
        with open(ESTATE_CACHE_PATH, 'r') as f:
            try:
                return json.load(f)
            except json.decoder.JSONDecodeError:
                return {}
    except FileNotFoundError:
        with open(ESTATE_CACHE_PATH, 'w'):
            pass
        return {}


def save_cache(cache: dict) -> None:
    with open(ESTATE_CACHE_PATH, 'w') as f:
        json.dump(cache, f)

# fill
cookies = {

}

# fill
headers = {

}

params = {
    'disposition': '1+1,1+kt,unusual',
    'max-price': '20000',
    'region': 'street Thákurova, Praha',
    'region-id': '122115',
    'region-type': 'street',
    'distance': '2',
}


# Filters were hardcoded into params. I'm lazy.
def fetch_recent_estates() -> dict:
    global SEARCH_URL, params, cookies, headers
    response = requests.get(url=SEARCH_URL,
                            params=params,
                            cookies=cookies,
                            headers=headers)

    soup = BeautifulSoup(response.content, "html.parser")
    ul_anchor = soup.find("ul", attrs={"data-e2e": "estates-list"})
    estate_items = ul_anchor.find_all("li", id=lambda x: x and x.startswith("estate-list-item-"))

    hash_url_map = {}

    for estate in estate_items:
        estate_hash = estate["id"].replace("estate-list-item-", "")

        a = estate.find("a", href=True)
        if not a:
            continue

        hash_url_map[estate_hash] = BASE_URL + a["href"]

    return hash_url_map


def fresh_estates() -> list[str]:
    hash_url_map = fetch_recent_estates()
    estate_cache = load_cache()

    fresh_hashes = set(hash_url_map) - set(estate_cache)

    estate_cache.update({h: 1 for h in fresh_hashes})
    save_cache(estate_cache)

    return [hash_url_map[h] for h in fresh_hashes]

