import random
import time
from pathlib import Path
from pprint import pprint

import requests
from requests_html import HTMLSession

baseurl = "https://www.bible.com/km/bible/85/"
baseurl = "https://www.bible.com/bible/142/"
# Chapter ref format for Bible.com "GEN.1"

#baseurl = "https://biblesa.co.za/bible/TSW08NO/"
#baseurl = "https://setswana.global.bible/bible/2b759e1caf81a2e3-01/"
basepath = Path("F:/GitHub/davidbaines/scraper/RNKSV/html/")


max_chapters = {"GEN":50, "EXO":40, "LEV":27, "NUM":36, "DEU":34, "JOS":24, "JDG":21, "RUT":4, "1SA":31, "2SA":24, "1KI":22, "2KI":25, "1CH":29, "2CH":36, "EZR":10, "NEH":13, "EST":10, "JOB":42, "PSA":150, "PRO":31, "ECC":12, "SNG":8, "ISA":66, "JER":52, "LAM":5, "EZK":48, "DAN":12, "HOS":14, "JOL":4, "AMO":9, "OBA":1, "JON":4, "MIC":7, "NAM":3, "HAB":3, "ZEP":3, "HAG":2, "ZEC":14, "MAL":3, "MAT":28, "MRK":16, "LUK":24, "JHN":21, "ACT":28, "ROM":16, "1CO":16, "2CO":13, "GAL":6, "EPH":6, "PHP":4, "COL":4, "1TH":5, "2TH":3, "1TI":6, "2TI":4, "TIT":3, "PHM":1, "HEB":13, "JAS":5, "1PE":5, "2PE":3, "1JN":5, "2JN":1, "3JN":1, "JUD":1, "REV":22}
books = [book for book in max_chapters]

all_chapters = []
for book in max_chapters:
    for chapter in range(1, max_chapters[book] + 1):
        all_chapters.append(f"{book}.{chapter}")

#pprint(all_chapters)

session = HTMLSession()


# Setswana URLcode
# for chapter in all_chapters[0:2]:
#     url = f"{baseurl}{chapter}/"
#     file = basepath /  f"{chapter}.html"
#     print(url, file, f"exists: {file.is_file()}")

#     if not file.is_file():    
#         r = session.get(url)
#         r.html.render()  # this call executes the js in the page
#         #r = requests.get(url, allow_redirects=True)
#         open(file, 'wb').write(r.content)
#         time.sleep(random.randrange(3,36))

# YouVersion Bible.com Code.
for chapter in all_chapters:
    url = f"{baseurl}{chapter}/"
    file = basepath /  f"{chapter}.html"
    #print(url, file, f"exists: {file.is_file()}")

    if not file.is_file():    
        print(f"Reading url: {url}")
        r = session.get(url)
        r.html.render()  # this call executes the js in the page
        time.sleep(5)
        r = requests.get(url, allow_redirects=True)
        open(file, 'wb').write(r.content)
        time.sleep(random.randrange(5,15))
    else:
        print(f"File {file.name} exists.")


#xpath = "/html/body/div[1]/app-root/app-bible-reader/div[2]/app-bible-column/div[2]/app-bible-passage"

#page = requests.get(links[0])

#print(page.text)