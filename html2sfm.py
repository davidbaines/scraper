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
    for vref in vrefs:
        book, chapter, _ = parse_vref(vref)
        max_chapters[book] = chapter
    return max_chapters


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


# def parse_html(html_file, usfm_data):
#     pattern = r"(?P<book_id>.{3})\.(?P<chapter>\d+).(?P<verse>\d+)"

#     with open(html_file, "r", encoding="utf-8") as f:
#         soup = BeautifulSoup(f, "lxml")

#     book_title = soup.head.title

#     book_id = None
#     for verse_span in soup.find_all("span"):
#         if verse_span.get("data-usfm"):
#             match = re.match(pattern, verse_span["data-usfm"])
#             if match:
#                 book_id = match.group("book_id")
#                 chapter = match.group("chapter")
#                 verse = match.group("verse")
#                 text = verse_span.text

#                 if book_id not in usfm_data:
#                     usfm_data[book_id] = {}
#                     print(f"Couldn't find book {book_id} in {usfm_data}")
#                 if chapter not in usfm_data[book_id]:
#                     usfm_data[book_id][chapter] = {}
#                     print(f"Couldn't chapter {chapter} in {usfm_data[book_id]}")

#                 usfm_data[book_id][chapter][verse] = text
#                 print(f"Added {book_id} {chapter}:{verse}   {text} ")

#     if not book_id:
#         print(f"Warning: Could not parse book ID from {html_file}. HTML content:")
#         print(soup.prettify())
#         exit()

#     if not book_title:
#         print(f"Warning: Could not parse book title from {html_file}. HTML content:")
#         print(soup.prettify())
#         exit()

#     return usfm_data


# def parse_html(html_file, usfm_data):
#     pattern = r"(?P<book_id>.{3})\.(?P<chapter>\d+).(?P<verse>\d+)"

#     with open(html_file, "r", encoding="utf-8") as f:
#         soup = BeautifulSoup(f, "lxml")

#     book_title = soup.head.title.string.split(" | ")[0]

#     book_id = None

#     for i, verse_span in enumerate(soup.find_all("span", attrs={"data-usfm": True}),1):
        
#         match = re.match(pattern, verse_span["data-usfm"])
#         if match:
#             book_id = match.group("book_id")
#             chapter = match.group("chapter")
#             verse = match.group("verse")

#             # Find the child span that contains the verse text
#             text_span = verse_span.find(
#                 "span",
#                 class_=lambda value: value
#                 and value.startswith("ChapterContent_content"),
#             )
#             if text_span:
#                 text = text_span.text.strip()  # Remove any leading/trailing whitespace

#                 if book_id not in usfm_data:
#                     usfm_data[book_id] = {}
#                 if chapter not in usfm_data[book_id]:
#                     usfm_data[book_id][chapter] = {}
#                 if verse in usfm_data[book_id][chapter]:
#                     print(f"{i} Overwriting would happen here.")
#                     #usfm_data[book_id][chapter][verse] = text
#                 elif verse not in usfm_data[book_id][chapter]:
#                     usfm_data[book_id][chapter][verse] = text
#                     print(f"{i}  Added {book_id} {chapter}:{verse}   {text} ")
#             else:
#                 print(
#                     f"Warning: Could not parse verse text from {verse_span}. HTML content:"
#                 )
#                 continue  # Skip this verse if its text couldn't be extracted

#     return usfm_data


def get_verse_text(verse_span):
    """
    Given a verse span, find all child spans with a class that starts with "ChapterContent_content",
    concatenate their text and return the result.
    """
    text_spans = verse_span.find_all("span", class_=lambda value: value and value.startswith("ChapterContent_content"))
    text = ' '.join(span.text for span in text_spans)
    return text.strip()  # Remove any leading/trailing whitespace

def parse_html(html_file, usfm_data):
    pattern = r"(?P<book_id>.{3})\.(?P<chapter>\d+).(?P<verse>\d+)"

    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    book_title = soup.head.title.string.split(" | ")[0]

    book_id = None

    for i, verse_span in enumerate(soup.find_all("span", attrs={"data-usfm": True}),1):
        match = re.match(pattern, verse_span["data-usfm"])
        if match:
            book_id = match.group("book_id")
            chapter = match.group("chapter")
            verse = match.group("verse")
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
                print(f"{i}  Added {book_id} {chapter}:{verse}   {text} ")

    if not book_id:
        print(f"Warning: Could not parse book ID from {html_file}. HTML content:")
        print(soup.prettify())
        exit()
    
    if not book_title:
        print(f"Warning: Could not parse book title from {html_file}. HTML content:")
        print(soup.prettify())
        exit()

    return usfm_data




def check_html_file(html_file):

    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    if soup.head.title == None:
        return False
    else:
        return True


def save_to_usfm(book_id, book_title, usfm_data, output_file):

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"\\id {book_id} - {book_title}\n")
        for chapter in sorted(usfm_data, key=int):
            f.write(f"\\c {chapter}\n")
            for verse in sorted(usfm_data[chapter], key=int):
                f.write(f"\\v {verse} {usfm_data[chapter][verse]}\n")


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


def process_book(input_folder, output_folder, book):

    # Output USFM data for each book
    filenames = {
        book: f"{i:02}{book}.sfm" for i, book in enumerate(get_max_chapters().keys(), 1)
    }
    output_file = Path(output_folder) / filenames[book]

    html_files = [
        html_file
        for html_file in Path(input_folder).glob(f"{book}_*.htm")
        if html_file.is_file
    ]

    usfm_data = {}

    # Now use this custom_sort function to sort the html_files.
    html_files = sorted(html_files, key=custom_sort)

    print(f"Found {len(html_files)} html files to process for book {book}.")

    for html_file in html_files:
        # print(f"processing file : {html_file}")

        usfm_data = parse_html(html_file, usfm_data)

        print(usfm_data)
        exit()

        # Merge book data into main data dictionary

        for chapter, verses in book_data[book_id].items():
            if chapter not in usfm_data[book_id]:
                usfm_data[book_id][chapter] = {}
            for verse, text in verses.items():
                usfm_data[book_id][chapter][verse] = text

        # Store book title
        book_titles[book_id] = book_title

    # Output USFM data for each book
    filenames = {
        book: f"{i:02}{book}.sfm" for i, book in enumerate(get_max_chapters().keys(), 1)
    }

    for book_id, book_data in usfm_data.items():

        output_file = Path(output_folder) / filenames[book_id]
        save_to_usfm(book_id, book_titles[book_id], book_data, output_file)


def main():
    project_id = "ABTAG01"
    input_path = Path(f"E:/Work/Pilot_projects/Ayta Mag Indi/{project_id}")
    save_path = Path(f"E:/Work/Pilot_projects/Ayta Mag Indi/projects/{project_id}")

    # Ensure the output directory exists
    os.makedirs(save_path, exist_ok=True)

    # Check html files.
    # failed_files = check_files(input_path)

    # Sample usage:
    process_book(input_path, save_path, "GEN")


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
