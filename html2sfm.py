import argparse
import os
import re
import time
from pathlib import Path, PurePath
from random import randint

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def get_vrefs():
    with open("F:/GitHub/silnlp/silnlp/assets/vref.txt") as vref_f:
        return [line.strip() for line in vref_f.readlines()]


def get_vref_dict() -> dict:
    vref_dict = {}
    vrefs = get_vrefs()
    for book, chapter,verse in parse_vref(vref):
        if book not in vref_dict:
            vref_dict[book] = {}
        if chapter not in vref_dict[book]:
            vref_dict[book][chapter] = []
        
        vref_dict[book][chapter].append(verse)
    return vref_dict


def get_bible_files(folder):
    bible_files = [file for file in folder.glob("*.txt")]
    return bible_files


def parse_vref(vref):
    vref_pattern = r"(?P<book>\w+)\s+(?P<chapter>\d+):(?P<verse>\d+)"
    match = re.match(vref_pattern, vref)

    if match:
        book = match.group("book")
        chapter = int(match.group("chapter"))
        verse = int(match.group("verse"))
        return book, chapter, verse
    else:
        raise ValueError(f"Invalid vref format: {vref}")


def get_max_chapters() -> dict:
    vrefs = get_vrefs()
    max_chapters = {}
    for vref in vrefs:  # vrefs should be global
        book, chapter, _ = parse_vref(vref)
        max_chapters[book] = chapter
    return max_chapters

def get_max_chapter(book) -> dict:
    vref_dict = get_vref_dict()
    return max(vref_dict[book])
    

def get_max_verse(book, chapter) -> int:
    vref_dict = get_vref_dict()
    return max(vref_dict[book][chapter])


def get_files_from_folder(folder,ext):
    files = [file for file in folder.glob(f"*{ext}") if file.is_file]
    return files


def download_url(url) -> None:

    # Create a Service object
    webdriver_service = Service("F:/Github/chromedriver.exe")

    # Pass the Service object into webdriver.Chrome()
    driver = webdriver.Chrome(service=webdriver_service)
    print(f"Downloading {url}")

    # Navigate to the page
    driver.get(url)
    time.sleep(5)

    # now the JavaScript-loaded data should be in the DOM
    # get the current page source
    html = driver.page_source

    # Close the browser
    driver.quit()
    return html


def simplify_html(html_file):
    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Remove all tags that do not contain visible text
    for tag in soup.find_all():
        if isinstance(tag, Tag) and tag.get_text(strip=True) == "":
            tag.decompose()

    return str(soup)


def get_verse_text(verse_span):
    """
    Given a verse span, find all child spans with a class that starts with "ChapterContent_content",
    concatenate their text and return the result.
    """
    text_spans = verse_span.find_all("span", class_=lambda value: value and value.startswith("ChapterContent_content"))
    text = ' '.join(span.text for span in text_spans).replace("   ", " ").replace("  "," ")

    return text.strip()  # Remove any leading/trailing whitespace


def parse_html(html_file, usfm_data):
    pattern = r"(?P<book_id>.{3})\.(?P<chapter>\d+).(?P<verse>\d+)"

    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    book_id = None

    for i, verse_span in enumerate(soup.find_all("span", attrs={"data-usfm": True}),1):
        match = re.match(pattern, verse_span["data-usfm"])
        if match:
            book_id = match.group("book_id")
            chapter = int(match.group("chapter"))
            verse = int(match.group("verse"))
            text = get_verse_text(verse_span)  # Extract the verse text

            if book_id not in usfm_data:
                usfm_data[book_id] = {}
            if chapter not in usfm_data[book_id]:
                usfm_data[book_id][chapter] = {}
            #if verse in usfm_data[book_id][chapter]:
            #    print(f"{i} Overwriting would happen here.")
            #    #usfm_data[book_id][chapter][verse] = text
            if verse not in usfm_data[book_id][chapter]:
                usfm_data[book_id][chapter][verse] = text
                #print(f"{i}  Added {book_id} {chapter}:{verse}   {text} ")

    if not book_id:
        print(f"Warning: Could not parse book ID from {html_file}. ")
        return None

    return usfm_data


def check_html_file(html_file):

    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    if soup.head.title == None:
        return False
    else:
        return True


def save_to_usfm(book_id, usfm_data, output_file):
    #print(usfm_data["GEN"][1])
    #exit()
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"\\id {book_id}\n")
        for chapter in sorted(usfm_data[book_id], key=int):
            f.write(f"\\c {chapter}\n")
            for verse in sorted(usfm_data[book_id][chapter], key=int):
                f.write(f"\\v {verse} {usfm_data[book_id][chapter][verse]}\n")


def custom_sort(html_file):
    """Sort function to sort filenames based on the numerical value in the filename."""
    return int(re.search(r"(\d+)\.htm$", html_file.name).group(1))


def check_files(input_folder):
    # Iterate over all HTML files in the input directory
    html_files = [
        html_file for html_file in Path(input_folder).glob("*.htm") if html_file.is_file
    ]

    # Now use this custom_sort function to sort the html_files.
    html_files = sorted(html_files, key=custom_sort)

    print(f"Found {len(html_files)} to check in {input_folder}")

    failed_files = [
        html_file for html_file in html_files if check_html_file(html_file) == False
    ]
    print(f"Couldn't parse these files:")
    for failed_file in failed_files:
        print(failed_file)

    return failed_files


def process_book(input_folder, output_file, book):

    usfm_data = {}

    # Iterate over all HTML files in the input directory
    html_files = [
        html_file for html_file in Path(input_folder).glob(f"{book}*.htm") if html_file.is_file
    ]
    
    # Now use this custom_sort function to sort the html_files.
    sorted_html_files = sorted(html_files, key=custom_sort)

    #print(f"Found {len(sorted_html_files)} html files to process for book {book}.")

    for sorted_html_file in sorted_html_files:
        # print(f"processing file : {html_file}")

        usfm_data = parse_html(sorted_html_file, usfm_data)

        #print(usfm_data)
        #exit()

    if usfm_data is not None:
        # Output USFM data for book
        save_to_usfm(book, usfm_data, output_file)


def main():

    project_id = "loz"
    downloaded_html_folder = Path(f"E:/Work/Pilot_projects/Lozi/html")
    sfm_folder = Path(f"E:/Work/Pilot_projects/Lozi/{project_id}") 
    max_chapters = get_max_chapters()

    # Ensure the output directory exists
    os.makedirs(sfm_folder, exist_ok=True)
    
    files = get_files_from_folder(downloaded_html_folder, "htm")
    print(f"Found {len(files)} usfm files ")
    book_set = {file.name[:3] for file in files}
    books = [book for book in max_chapters.keys() if book in book_set]

    print(books)
    
    for book in books:
        book_number = list(max_chapters.keys()).index(book) + 1
        sfm_file = sfm_folder / f"{book_number:02}{book}.sfm"
        print(f"Process book: {book_number:02}_{book} to save as {sfm_file}")
        process_book(downloaded_html_folder, sfm_file, book)


if __name__ == "__main__":
    main()


# def process_books(input_folder, output_folder ):
#     book_titles = {}
#     usfm_data = {}

#     # Iterate over all HTML files in the input directory
#     html_files = [
#         html_file for html_file in Path(input_folder).glob("*.htm") if html_file.is_file
#     ]

#     # Now use this custom_sort function to sort the html_files.
#     html_files = sorted(html_files, key=custom_sort)

#     print(f"Found {len(html_files)} html files to process.")

#     for html_file in html_files:
#         # print(f"processing file : {html_file}")

#         usfm_data = parse_html(html_file, usfm_data)

#         # Merge book data into main data dictionary
#         if book_id not in usfm_data:
#             usfm_data[book_id] = {}
#         for chapter, verses in book_data[book_id].items():
#             if chapter not in usfm_data[book_id]:
#                 usfm_data[book_id][chapter] = {}
#             for verse, text in verses.items():
#                 usfm_data[book_id][chapter][verse] = text

#         # Store book title
#         book_titles[book_id] = book_title

#     # Output USFM data for each book
#     filenames = {book : f"{i:02}{book}.sfm" for i, book in enumerate(get_max_chapters().keys(),1)}

#     for book_id, book_data in usfm_data.items():

#         output_file = Path(output_folder) / filenames[book_id]
#         save_to_usfm(book_id, book_titles[book_id], book_data, output_file)
