import random
import time
from pathlib import Path
from pprint import pprint

import requests
from requests_html import HTMLSession

baseurl = "https://biblesa.co.za/bible/TSW08NO/"
baseurl = "https://setswana.global.bible/bible/2b759e1caf81a2e3-01/"
basepath = Path("F:/GitHub/davidbaines/scraper/html")

books = ['GEN', 'EXO', 'LEV', 'NUM', 'DEU', 'JOS', 'JDG', 'RUT', '1SA', '2SA', '1KI', '2KI', '1CH', '2CH', 'EZR', 'NEH', 'EST', 'JOB', 'PSA', 'PRO', 'ECC', 'SNG', 'ISA', 'JER', 'LAM', 'EZK', 'DAN', 'HOS', 'JOL', 'AMO', 'OBA', 'JON', 'MIC', 'NAM', 'HAB', 'ZEP', 'HAG', 'ZEC', 'MAL'
'MAT', 'MRK', 'LUK', 'JHN', 'ACT', 'ROM', '1CO', '2CO', 'GAL', 'EPH', 'PHP', 'COL', '1TH', '2TH', '1TI', '2TI', 'TIT', 'PHM', 'HEB', 'JAS', '1PE', '2PE', '1JN', '2JN', '3JN', 'JUD', 'REV']

chapters = [50, 40, 27, 36, 34, 24, 21, 4, 31 ]

all_chapters = []
for i, max_chapter in enumerate(chapters):
    book = books[i]
    for chapter in range(1, max_chapter + 1):
        all_chapters.append(f"{book}.{chapter}")

#pprint(all_chapters)
session = HTMLSession()

for chapter in all_chapters[0:2]:
    url = f"{baseurl}{chapter}/"
    file = basepath /  f"{chapter}.html"
    print(url, file, f"exists: {file.is_file()}")

    if not file.is_file():    
        r = session.get(url)
        r.html.render()  # this call executes the js in the page
        #r = requests.get(url, allow_redirects=True)
        open(file, 'wb').write(r.content)
        time.sleep(random.randrange(3,36))
        
#xpath = "/html/body/div[1]/app-root/app-bible-reader/div[2]/app-bible-column/div[2]/app-bible-passage"

#page = requests.get(links[0])

#print(page.text)