"""
Модуль, использованный для загрузки страниц Викисловаря с латинскими глаголами. Список страниц Latin verbs.txt собран вручную.
"""

import urllib.request as urr
import urllib.parse as urp
import urllib.error as ure
from time import sleep
import os

def rob_wiktionary(verb, write_to_file=True):
    # прикинемся браузером
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}

    source = "https://en.wiktionary.org/wiki/" + urp.quote(verb)
    request = urr.Request(source, headers=HEADERS)
    try:
        response = urr.urlopen(request)
    except ure.HTTPError as e:
        print(e)
        exit()
    contents = response.read().decode("utf8")

    if write_to_file:
        with open(verbdir + verb + ".html", "w", encoding="utf8") as fout:
            fout.write(contents)

    return contents

def load_verbs():
    # загружаем список глаголов
    print('Loading verbs...')
    verbs = []
    seen = []
    for file in os.listdir(verbdir):
        if file.endswith(".html"):
            seen.append(file.split('.')[0])
    with open ("Latin verbs.txt", 'r', encoding='utf8') as fin:
        for line in fin:
            if line.strip() not in seen:
                verbs.append(line.strip())

    print(f"Scanning {len(verbs)} verbs...")
    for verb in verbs:
        rob_wiktionary(verb)
        sleep(3)

dir_path = os.path.dirname(os.path.realpath(__file__))
verbdir = dir_path + '\\Verbs\\'