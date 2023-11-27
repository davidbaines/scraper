import time
import argparse
# from inspect import getmembers
from pathlib import Path, PurePath
from random import randint
import re
from shutil import copyfile
import itertools
#from xvfbwrapper import Xvfb

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

def get_vrefs():
    with open("F:/GitHub/silnlp/silnlp/assets/vref.txt") as vref_f:
        return [line.strip() for line in vref_f.readlines()]
    

def get_bible_files(folder):
    bible_files = [file for file in folder.glob('*.txt')]
    return bible_files


def parse_vref(vref):
    vref_pattern = r'(?P<book>\w+)\s+(?P<chapter>\d+):(?P<verse>\d+)'
    match = re.match(vref_pattern, vref)

    if match:
        book = match.group('book')
        chapter = int(match.group('chapter'))
        verse = int(match.group('verse'))
        return book, chapter, verse
    else:
        raise ValueError(f"Invalid vref format: {vref}")


def get_max_chapters() -> dict:
    vrefs = get_vrefs()
    max_chapters = {}
    for vref in vrefs:
        book, chapter, _ = parse_vref(vref)
        max_chapters[book] = chapter
    return max_chapters


def print_table(rows):

    for arg, value in rows:
        if isinstance(value, PurePath):
            print(
                f"{str(arg):<30} : {str(value):<41} | {str(type(value)):<30} | {str(value.exists()):>6}"
            )
        else:
            print(f"{str(arg):<30} : {str(value):<41} | {str(type(value)):<30}")

    print()


def show_attrs(obj):

    arg_rows = [(k, v) for k, v in obj.__dict__.items() if v is not None]
    print_table(arg_rows)


def download_chapter(driver, baseurl, bible_id_no, book, chapter , project_id, html_file):
    url = f"{baseurl}/{bible_id_no}/{book}.{chapter}.{project_id}".replace("//", "/") 
    
    # Navigate to the page
    driver.get(url)
    time.sleep(5)

    html = driver.page_source

    with open(html_file, 'w', encoding='utf-8') as f:
         f.write(html)

    return html




def main() -> None:

    parser = argparse.ArgumentParser(description="Scrape from jarvascript site.")
    parser.add_argument(
        "--debug",
        default=False,
        action="store_true",
        help="Show information about the environment variables and arguments.",
    )
    parser.add_argument(
        "--books", metavar="books", nargs="+", default=[], help="The books to translate; e.g., 'NT', 'OT', 'GEN,EXO'"
    )
    args = parser.parse_args()
    
    if args.debug:
        show_attrs(driver)

    max_chapters = get_max_chapters()
    all_books =  [book for book in get_max_chapters().keys()]

    ot_books = all_books[0:39]
    nt_books = all_books[39:66]
    dc_books = all_books[66:len(all_books)]

    # print(all_books)
    # print(ot_books)
    # print(nt_books)
    # print(dc_books)
    # exit()

    if not args.books:
        books = all_books
    else:
        books = []
        if 'OT' in args.books:
            books.extend(ot_books)
        if 'NT' in args.books:
            books.extend(nt_books)
        if 'DC' in args.books:
            books.extend(dc_books)
        
        books.extend([book for book in args.books if len(book) == 3 and book not in books and book in all_books])
    chapters = [max_chapters[book] for book in books]
    
    print(f"Argument books = {books}")
    print(f"Books to download:\n{books}")
    print(f"There are a total of {len(max_chapters)} books.")
    print(f"There are {len(books)} books to download:\n{books}")
    print(f"There are {sum(chapters)} chapters to download in total.")
    
    baseurl = "https://www.bible.com/bible/"
    bible_id_no = "2195"
    project_id = "ABTAG01"
    baseurl = "https://www.bible.com/si/bible/"
    bible_id_no = "3157"
    project_id = "dzoD"

    baseurl = "https://www.bible.com/si/bible/"
    bible_id_no = "3157"
    project_id = "dzoD"

    url = "https://www.bible.com/am/bible/825/REV.17.Lozi09"
    baseurl = "https://www.bible.com/am/bible/"
    bible_id_no = "825"
    project_id = "Lozi09"

    # html = download_chapter(baseurl, bible_id_no, book, chapter, project_id)
    save_path = Path(f"E:/Work/Pilot_projects/Lozi/html")

#    print(f"Will save to {save_path}. These files already exist there:")
#    existing_files = save_path.glob("*.htm")
#    for existing_file in existing_files:
#        print(existing_file.name)

    
    # Create a Service object
    webdriver_service = Service("F:/Github/chromedriver.exe")

    #options = Options()
    #options.add_argument("--headless")

    # Pass the Service object into webdriver.Chrome()
    driver = webdriver.Chrome(service=webdriver_service) #, options=options)

    chapter = 1

    for book in books:
        last_chapter_in_book =  max_chapters[book]
        print(f"last_chapter in book {book} : {last_chapter_in_book}")
        
        for chapter in range(1,last_chapter_in_book+1):
        
            url = f"{baseurl}/{bible_id_no}/{book}.{chapter}.{project_id}".replace("//", "/") 
            html_filename = f"{book}_{chapter}.htm"
            
            html_file = save_path / html_filename
            if not html_file.is_file():
                print(f"File {html_file} is not present Downloading: ")
                download_chapter(driver, baseurl, bible_id_no, book, chapter , project_id, html_file)
            
    driver.quit()

if __name__ == "__main__":
    main()


    # book = "PSA"
    # chapter = 109

    # html = download_chapter(baseurl, bible_id_no, book, chapter, project_id)
    # save_path = Path(f"E:/Work/Pilot_projects/Ayta Mag Indi/{project_id}")
    # html_filename = f"{book}_{chapter}.htm"        
    # html_file = save_path / html_filename
    # with open(html_file, 'w', encoding='utf-8') as f:
    #     f.write(html)
    # exit()



    # # Navigate to the page
    #         driver.get(url)
    #         time.sleep(5)
    
    #         # now the JavaScript-loaded data should be in the DOM
    #         # get the current page source
    #         html = driver.page_source

    #         # save the HTML to a file
    #         with open(html_file, 'w', encoding='utf-8') as f:
    #             f.write(html)

    #         # Pretend to be human
    #         total_delay = randint(5, 15)
                        
    #         # Get the total height of the web page
    #         total_height = int(driver.execute_script("return document.body.scrollHeight"))

    #         # The height of the portion to scroll each second
    #         portion_height = total_height / total_delay

    #         for current_delay in range(total_delay):
    #             driver.execute_script(f"window.scrollBy(0, {portion_height});")
    #             time.sleep(1)  # wait for 1 second
