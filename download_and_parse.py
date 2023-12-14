import argparse
import os
import re
import time
from pathlib import Path
from random import randrange

import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait

BIBLE = {
    "GEN": 50,
    "EXO": 40,
    "LEV": 27,
    "NUM": 36,
    "DEU": 34,
    "JOS": 24,
    "JDG": 21,
    "RUT": 4,
    "1SA": 31,
    "2SA": 24,
    "1KI": 22,
    "2KI": 25,
    "1CH": 29,
    "2CH": 36,
    "EZR": 10,
    "NEH": 13,
    "EST": 10,
    "JOB": 42,
    "PSA": 150,
    "PRO": 31,
    "ECC": 12,
    "SNG": 8,
    "ISA": 66,
    "JER": 52,
    "LAM": 5,
    "EZK": 48,
    "DAN": 12,
    "HOS": 14,
    "JOL": 4,
    "AMO": 9,
    "OBA": 1,
    "JON": 4,
    "MIC": 7,
    "NAM": 3,
    "HAB": 3,
    "ZEP": 3,
    "HAG": 2,
    "ZEC": 14,
    "MAL": 3,
    "MAT": 28,
    "MRK": 16,
    "LUK": 24,
    "JHN": 21,
    "ACT": 28,
    "ROM": 16,
    "1CO": 16,
    "2CO": 13,
    "GAL": 6,
    "EPH": 6,
    "PHP": 4,
    "COL": 4,
    "1TH": 5,
    "2TH": 3,
    "1TI": 6,
    "2TI": 4,
    "TIT": 3,
    "PHM": 1,
    "HEB": 13,
    "JAS": 5,
    "1PE": 5,
    "2PE": 3,
    "1JN": 5,
    "2JN": 1,
    "3JN": 1,
    "JUD": 1,
    "REV": 22,
}
# d1 = dict(list(d.items())[len(d)//2:])
# d2 = dict(list(d.items())[:len(d)//2])

OT = dict(list(BIBLE.items())[0:39])
NT = dict(list(BIBLE.items())[39:])


def get_vrefs():
    with open("F:/GitHub/silnlp/silnlp/assets/vref.txt") as vref_f:
        return [line.strip() for line in vref_f.readlines()]


def get_vref_dict() -> dict:
    vref_dict = {}
    vrefs = get_vrefs()
    for book, chapter, verse in parse_vref(vref):
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


def get_files_from_folder(folder, ext):
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
    text_spans = verse_span.find_all(
        "span",
        class_=lambda value: value and value.startswith("ChapterContent_content"),
    )
    text = (
        " ".join(span.text for span in text_spans)
        .replace("   ", " ")
        .replace("  ", " ")
    )

    return text.strip()  # Remove any leading and trailing whitespace


def parse_html(html_file, usfm_data):
    pattern = r"(?P<book_id>.{3})\.(?P<chapter>\d+).(?P<verse>\d+)"

    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    book_id = None

    for i, verse_span in enumerate(soup.find_all("span", attrs={"data-usfm": True}), 1):
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
            # if verse in usfm_data[book_id][chapter]:
            #    print(f"{i} Overwriting would happen here.")
            #    #usfm_data[book_id][chapter][verse] = text
            if verse not in usfm_data[book_id][chapter]:
                usfm_data[book_id][chapter][verse] = text
                # print(f"{i}  Added {book_id} {chapter}:{verse}   {text} ")

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
    # print(usfm_data["GEN"][1])

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"\\id {book_id}\n")
        for chapter in sorted(usfm_data[book_id], key=int):
            f.write(f"\\c {chapter}\n")
            for verse in sorted(usfm_data[book_id][chapter], key=int):
                f.write(f"\\v {verse} {usfm_data[book_id][chapter][verse]}\n")


def custom_sort(html_file):
    """Sort function to sort filenames based on the numerical value in the filename."""
    return int(re.search(r"(\d+)\.html+$", html_file.name).group(1))


def check_html_files(html_files):
    # Now use this custom_sort function to sort the html_files.
    html_files = sorted(html_files, key=custom_sort)

    # print(f"Found {len(html_files)} to check.")

    failed_files = [
        html_file for html_file in html_files if check_html_file(html_file) == False
    ]
    print(f"Couldn't parse these files:")
    for failed_file in failed_files:
        print(failed_file)

    return failed_files


def xor(str1, str2):
    return bool(str1) ^ bool(str2)


def process_book(input_folder, output_file, book, file_ext):
    usfm_data = {}

    html_files = [
        html_file
        for html_file in Path(input_folder).glob(f"{book}*.{file_ext}")
        if html_file.is_file
    ]

    # Now use this custom_sort function to sort the html_files.
    sorted_html_files = sorted(html_files, key=custom_sort)

    print(f"Found {len(sorted_html_files)} html files to process for book {book}.")

    for sorted_html_file in sorted_html_files:
        print(f"processing file : {sorted_html_file}")

        usfm_data = parse_html(sorted_html_file, usfm_data)

    if usfm_data is not None:
        # Output USFM data for book
        save_to_usfm(book, usfm_data, output_file)


def save_page(url, file):
    session = HTMLSession()
    print(f"Reading url: {url}")
    r = session.get(url)
    r.html.render()  # this call executes the js in the page
    time.sleep(5)
    r = requests.get(url, allow_redirects=True)
    open(file, "wb").write(r.content)


def scrape(baseurl, html_folder, chapters_to_download):
    """Download the html for the books and chapters passed in as a dictionary of book:max_chapter."""

    if not baseurl.endswith("/"):
        raise RuntimeError(
            f"The baseurl passed to scrape is {baseurl}. It must end with a /"
        )

    # Chapter ref format for Bible.com "GEN.1"
    # baseurl = "https://biblesa.co.za/bible/TSW08NO/"
    # baseurl = "https://setswana.global.bible/bible/2b759e1caf81a2e3-01/"

    # YouVersion Bible.com Code.
    for chapter in chapters_to_download:
        url = f"{baseurl}{chapter}/"
        file = html_folder / f"{chapter}.html"
        # print(url, file, f"exists: {file.is_file()}")

        if not file.is_file():
            time.sleep(randrange(5, 15))
            save_page(url, file)
        else:
            print(f"File {file.name} exists.")

    # pprint(all_chapters)


def html2sfm(html_folder, sfm_folder, html_file_ext, books_to_skip):
    max_chapters = get_max_chapters()
    files = get_files_from_folder(html_folder, html_file_ext)
    print(f"Found {len(files)} {html_file_ext} files ")
    book_set = {file.name[:3] for file in files}
    books = [
        book
        for book in max_chapters.keys()
        if book in book_set and book not in books_to_skip
    ]
    print(books)
    # print(files)

    for book in books:
        book_number = list(max_chapters.keys()).index(book) + 1
        sfm_file = sfm_folder / f"{book_number:02}{book}.sfm"
        if sfm_file.is_file():
            print(f"SFM for {book} already exists. Skipping.")
            continue

        print(f"Process book: {book_number:02} {book} to save as {sfm_file}")
        process_book(html_folder, sfm_file, book, file_ext=html_file_ext)


def write_settings_file(language_name, iso_code, sfm_folder):
    settings = f'<ScriptureText>\n  <Language>{language_name}</Language>\n  <Encoding>65001</Encoding>\n  <LanguageIsoCode>{iso_code}:::</LanguageIsoCode>\n  <Versification>4</Versification>\n  <Naming PrePart="" PostPart=".SFM" BookNameForm="41MAT" />\n</ScriptureText>'
    settings_file = sfm_folder / "Settings.xml"

    if settings_file.is_file():
        print(f"Settings file {settings_file} already exists.")
    else:
        with open(settings_file, "w", encoding="utf-8") as f_out:
            f_out.write(settings)
        print(
            f"Wrote this into the Settings.xml file: {settings_file}\n\n{settings}\n\n"
        )


def main():
    parser = argparse.ArgumentParser(description="Convert html files to sfm files")
    parser.add_argument(
        "folder",
        type=Path,
        help="The project folder for the output.",
    )
    parser.add_argument(
        "number",
        type=int,
        help="The number of the Bible to download.",
    )
    parser.add_argument(
        "--language",
        type=str,
        help="The language name - for the Settings.xml file both language name and iso_code are required.",
    )
    parser.add_argument(
        "--iso",
        type=str,
        help="The iso code for the language. https://en.wikipedia.org/wiki/ISO_639-3/",
    )
    parser.add_argument(
        "--books",
        metavar="books",
        nargs="+",
        default=[],
        help="The books to download and parse; e.g., 'NT', 'OT', 'GEN EXO'",
    )
    parser.add_argument(
        "--chapters",
        metavar="chapters",
        nargs="+",
        default=[],
        help="In combination with books - a list of chapters to download.",
    )

    args = parser.parse_args()
    number = int(args.number)

    books = args.books if args.books else [book for book in BIBLE]
    chapters = [int(chapter) for chapter in args.chapters] if args.chapters else None

    chapters_to_download = []

    if chapters:
        for book in books:
            for chapter in chapters:
                chapters_to_download.append(f"{book}.{chapter}")
    else:
        for book in books:
            for chapter in range(1, BIBLE[book] + 1):
                chapters_to_download.append(f"{book}.{chapter}")

    baseurl = f"https://www.bible.com/en-GB/bible/{number}/"

    folder = Path(args.folder)
    html_folder = folder / "html"
    sfm_folder = folder / "sfm"

    project_folders = [folder, html_folder, sfm_folder]
    for project_folder in project_folders:
        # Ensure the directory exists and create it if necessary
        if not project_folder.is_dir():
            print(f"Creating folder for output: {project_folder}")
            os.makedirs(project_folder, exist_ok=True)

    print(chapters_to_download)
    scrape(baseurl, html_folder, chapters_to_download)

    sfm_files = get_files_from_folder(sfm_folder,"sfm")
    existing_books = [sfm_file.name[2:6] for sfm_file in sfm_files]
    
    html2sfm(html_folder, sfm_folder, html_file_ext="html", books_to_skip=existing_books)

    if args.language and args.iso:
        write_settings_file(args.language, args.iso, sfm_folder)

    elif args.language or args.iso:
        print(
            f"Both Language name and iso code need to be specified in order to write the Settings.xml file."
        )

    else:
        print(
            f"No Language name or iso code specified, Settings.xml file wasn't written. If you specify both a minimal Settings file can be written, enabling extraction in SIL NLP."
        )


if __name__ == "__main__":
    main()
