import requests
import json
from bs4 import BeautifulSoup

BASE_URL   = "https://www.sreality.cz"
SEARCH_URL = "https://www.sreality.cz/en/search/apartments/praha"

ESTATE_CACHE_PATH = "estate_cache.json"


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


cookies = {
    'cw_util': 'eyJyaSI6Ijc3Yzc4OWJiYTVlZGRhMmJlYjVlODQ3YzNjZmVhMWMwIn0',
    'cmpreferrer': 'https://www.google.com/',
    'qusnyQusny': '1',
    'szncmpone': '1',
    'euconsent-v2': 'CQbZEAAQbZEAAD3ACQCSCNFsAP_gAEPgAATIJNQJgAFAAQAAqABkAEAAKAAZAA0ACSAEwAJwAWwAvwBhAGIAQEAggCEAEUAI4ATgAoQBxADuAIQAUgA04COgE2gKkAVkAtwBeYDGQGWAMuAf4BAcCMwEmgSrgKgAVABAADIAGgATAAxAB-AEIAI4ATgA7gCEAEWATaAqQBWQC3AF5gMsAZcBKsAA.YAAAAAAAAWAA',
    'udid': '019ab736-14a3-7e3f-a6fb-02cba70eded4@1768497892581',
    'sid': 'id=3293735348527298809|t=1765914134.736|te=1768582590.713|c=521A341CFE35AAE3A85E3A33A3219335',
    'szncsr': '1768584326',
    'c.seznam.cz|sznlbr': 'c4e852b989f0291588e96b726e3bce4614824dd387a928406247028f32df980c',
    'hint-switch-mode-seen': 'true',
    'lastsrch': '"{}"',
    '__cw_snc': '1',
    'sznlbr': '15def08c3ac5f87261168e48b61eedda5b3ae412fc1d001868533aaf2f75f067',
    'last-redirect': '1',
    'h.seznam.cz|sznlbr': '5c046c6f1fd9b1a89d05eeaee1e497c7c269e2c70d832ae95df5b66166693748',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Connection': 'keep-alive',
    # 'Cookie': 'cw_util=eyJyaSI6Ijc3Yzc4OWJiYTVlZGRhMmJlYjVlODQ3YzNjZmVhMWMwIn0; cmpreferrer=https://www.google.com/; qusnyQusny=1; szncmpone=1; euconsent-v2=CQbZEAAQbZEAAD3ACQCSCNFsAP_gAEPgAATIJNQJgAFAAQAAqABkAEAAKAAZAA0ACSAEwAJwAWwAvwBhAGIAQEAggCEAEUAI4ATgAoQBxADuAIQAUgA04COgE2gKkAVkAtwBeYDGQGWAMuAf4BAcCMwEmgSrgKgAVABAADIAGgATAAxAB-AEIAI4ATgA7gCEAEWATaAqQBWQC3AF5gMsAZcBKsAA.YAAAAAAAAWAA; udid=019ab736-14a3-7e3f-a6fb-02cba70eded4@1768497892581; sid=id=3293735348527298809|t=1765914134.736|te=1768582590.713|c=521A341CFE35AAE3A85E3A33A3219335; szncsr=1768584326; c.seznam.cz|sznlbr=c4e852b989f0291588e96b726e3bce4614824dd387a928406247028f32df980c; hint-switch-mode-seen=true; lastsrch="{}"; __cw_snc=1; sznlbr=15def08c3ac5f87261168e48b61eedda5b3ae412fc1d001868533aaf2f75f067; last-redirect=1; h.seznam.cz|sznlbr=5c046c6f1fd9b1a89d05eeaee1e497c7c269e2c70d832ae95df5b66166693748',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Priority': 'u=0, i',
    # Requests doesn't support trailers
    # 'TE': 'trailers',
}

params = {
    'disposition': '1+1,1+kt,unusual',
    'max-price': '17000',
    'region': 'street Thákurova, Praha',
    'region-id': '122115',
    'region-type': 'street',
    'distance': '10',
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


if __name__ == "__main__":
    print(fresh_estates())
