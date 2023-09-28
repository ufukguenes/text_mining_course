import re

from newspaper import Article
import difflib

import requests
from bs4 import BeautifulSoup
import webbrowser

# we are comparing two web scraping algorithms: newspaper3k and beautifoul soup 4
# how matching works
# - not minimal
# - how it finds the common substring
# differences between 2 example texts
# ratio show


def download_html(url):
    try:
        # cookie = dict(BCPermissionLevel='PERSONAL')
        headers = {'User-Agent': 'Mozilla/s user-agent'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will check for status code 200 (OK)
        return response.text
    except requests.HTTPError as http_err:
        raise RuntimeError(f"HTTP error occurred: {response.status_code}")
    except Exception as err:
        raise RuntimeError(f"An error occurred: {err}")


def extract_title_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string if soup.title else "No title found"

    # assuming that the text is within paragraph tags
    paragraphs = soup.find_all('p')
    text = ' '.join([para.text for para in paragraphs])

    return title, text


def get_with_bs4(url):
    html = download_html(url)
    title, text = extract_title_text(html)
    return title, text


def get_with_np3k(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.title, article.text


# Sample usage:
urls = [
    'https://www.leprogres.fr/economie/2023/09/25/cinq-questions-sur-la-nouvelle-indemnite-carburant-annoncee-par-emmanuel-macron',
    'https://actu.fr/auvergne-rhone-alpes/lyon_69123/meteo-a-lyon-un-pic-de-chaleur-anormal-arrive-jusqu-a-30-c-les-previsions_60127288.html',
    'https://www.lemonde.fr/sciences/article/2023/09/19/de-tres-precises-gravures-prehistoriques-en-namibie_6190002_1650684.html',
    'https://www.lemonde.fr/sciences/article/2023/09/24/le-placozoaire-ce-minuscule-animal-a-l-origine-de-nos-neurones_6190724_1650684.html',
    'https://www.leprogres.fr/education/2023/09/25/manque-d-enseignants-pourquoi-le-recrutement-de-professeurs-via-pole-emploi-fait-debat',
    'https://www.nytimes.com/2023/09/22/us/politics/us-china-economic-dialogue.html'
]
ratios_pre = []
ratios_post = []

def clean_up(text: str):
    text = text.replace("\xa0", " ")
    text = text.replace("\r\n", " ")
    text = text.replace("\n", " ")
    text = text.replace("\r", " ")
    text = text.replace("\t", " ")
    text = text.replace("  ", " ")
    return text


for url in urls:
    bs4_title, bs4_text = get_with_bs4(url)
    np3k_title, np3k_text = get_with_np3k(url)

    matcher = difflib.SequenceMatcher()

    matcher.set_seqs(bs4_text, np3k_text)
    ratios_pre.append(matcher.ratio())
    print(f"pre text clean up ratio {matcher.ratio()}")

    bs4_text = clean_up(bs4_text)
    np3k_text = clean_up(np3k_text)

    matcher.set_seqs(bs4_text, np3k_text)
    ratios_post.append(matcher.ratio())
    print(f"post text clean up ratio {matcher.ratio()}")


    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue

        print('{:7}   a[{}:{}] --> b[{}:{}] {!r:>8} --> {!r}'.format(
            tag, i1, i2, j1, j2, bs4_text[i1:i2], np3k_text[j1:j2]))
