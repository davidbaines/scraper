import time
import argparse
# from inspect import getmembers
from pathlib import Path, PurePath
from random import randint
import re
from shutil import copyfile
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def download_url(url, html_file):
        
    # Create a Service object
    webdriver_service = Service("F:/Github/chromedriver.exe")

    # Pass the Service object into webdriver.Chrome()
    driver = webdriver.Chrome(service=webdriver_service)
    
    # Navigate to the page
    driver.get(url)
    time.sleep(5)
    html = driver.page_source

    with open(html_file, 'w', encoding='utf-8') as f:
         f.write(html)

    driver.quit()

    return html

def get_img_list(response):

    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')
    urls = [img['src'] for img in img_tags]            
            
    return urls


def save_urls(urls,file):
    with open(file, 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(url + "\n")

def main() -> None:

    parser = argparse.ArgumentParser(description="Scrape from javascript site.")
    parser.add_argument(
        "site", 
        help="Site to scrape.",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show information about the environment variables and arguments.",
    )

    args = parser.parse_args()
    
    if args.debug:
        print(f"Scraping site {args.site}")
    
    url = args.site
    pages = [no for no in range(2,181)]
    #print(pages)
    urls = [f"{args.site}page/{page}/" for page in pages] 
    #print(f"Will search these urls: {urls}")

    save_path = Path(f"F:/Temp/Sites/image_urls.txt")

    image_urls = []

    for url in urls:
        image_urls.extend(get_img_list(requests.get(url)))

    image_set = set(image_urls)

    #Save list.

    exit()

    # Create a Service object
    webdriver_service = Service("F:/Github/chromedriver.exe")

    # Pass the Service object into webdriver.Chrome()
    driver = webdriver.Chrome(service=webdriver_service)

    baseurl = args.site
    no = "2"

    # html = download_chapter(baseurl, bible_id_no, book, chapter, project_id)
    save_path = Path(f"F:/Temp/Sites/")

#    print(f"Will save to {save_path}. These files already exist there:")
#    existing_files = save_path.glob("*.htm")
#    for existing_file in existing_files:
#        print(existing_file.name)

    pages = [no for no in range(2,14)]
    print(f"{[pages]}")

    for page in pages:
        
            url = f"{args.site}{page}/"
            html_filename = f"page{page}"
            html_file = save_path / html_filename
            if not html_file.is_file():
                print(f"File {html_file} is not present Downloading: ")
                # Navigate to the page
                driver.get(url)

                # Give time to load
                time.sleep(5)
                html = driver.page_source
                
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html)

                print(driver.find_elements('img'))
                
                # Locate the data and extract it
                # element = driver.find_element_by_id("some_id") # or find_element(s)_by_class_name, etc.

                # element = driver.find_element_by_id("h1")
                # element = driver.find_element_by_any("p")
                # data = element.text  # or get_attribute("href"), etc.


    driver.quit()





if __name__ == "__main__":
    main()
