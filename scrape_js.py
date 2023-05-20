import time
import argparse
# from inspect import getmembers
from pathlib import Path, PurePath
from random import randint
import re
# from types import FunctionType

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


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


def main() -> None:

    parser = argparse.ArgumentParser(description="Scrape from jarvascript site.")
    parser.add_argument(
        "--debug",
        default=False,
        action="store_true",
        help="Show information about the environment variables and arguments.",
    )

    args = parser.parse_args()
    
    if args.debug:
        show_attrs(driver)
        max_chapters = get_max_chapters()
        bible_chapters = {}
        
        tob_seen = False
        for book, chapter in max_chapters.items():
            if book == "TOB":
                tob_seen = True
            if not tob_seen:
                bible_chapters[book] = chapter

        print(bible_chapters)
        exit()


    # Create a Service object
    webdriver_service = Service("F:/Github/chromedriver.exe")

    # Pass the Service object into webdriver.Chrome()
    driver = webdriver.Chrome(service=webdriver_service)
    
    max_chapters = get_max_chapters()
    bible_chapters = {}
    
    tob_seen = False
    for book, chapter in max_chapters.items():
        if book == "TOB":
            tob_seen = True
        if not tob_seen:
            bible_chapters[book] = chapter

    baseurl = "https://www.bible.com/bible/"
    bible_id_no = "2195"
    project_id = "ABTAG01"
    
    save_path = Path(f"E:/Work/Pilot_projects/Ayta Mag Indi/{project_id}")
    
    chapter = 1
    for book in bible_chapters.keys():
        last_chapter_in_book =  bible_chapters[book]
        for chapter in range(1,last_chapter_in_book):
        
            url = f"{baseurl}/{bible_id_no}/{book}.{chapter}.{project_id}".replace("//", "/") 
            html_filename = f"{book}_{chapter}_{project_id}.htm"
            
            html_file = save_path / html_filename
            if html_file.is_file():
                continue
            else:
                print(f"Downloading {book}:{chapter}")
            
            # Navigate to the page
            driver.get(url)
            time.sleep(5)
    
            # now the JavaScript-loaded data should be in the DOM
            # get the current page source
            html = driver.page_source

            # save the HTML to a file
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html)

            # Pretend to be human
            total_delay = randint(5, 45)
                        
            # Get the total height of the web page
            total_height = int(driver.execute_script("return document.body.scrollHeight"))

            # The height of the portion to scroll each second
            portion_height = total_height / total_delay

            for current_delay in range(total_delay):
                driver.execute_script(f"window.scrollBy(0, {portion_height});")
                time.sleep(1)  # wait for 1 second

    # Locate the data and extract it
    # element = driver.find_element_by_id("some_id") # or find_element(s)_by_class_name, etc.

#    element = driver.find_element_by_id("h1")
    # element = driver.find_element_by_any("p")
#    data = element.text  # or get_attribute("href"), etc.

    # Store the data
#   print(data)

    # Close the browser
    driver.quit()


if __name__ == "__main__":
    main()
