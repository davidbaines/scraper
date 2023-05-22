from bs4 import BeautifulSoup, Tag
import os
from pathlib import Path


def simplify_html(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Remove all tags that do not contain visible text
    for tag in soup.find_all():
        if isinstance(tag, Tag) and tag.get_text(strip=True) == '':
            tag.decompose()

    return str(soup)

def main():
    project_id = "ABTAG01"    
    input_path = Path(f"E:/Work/Pilot_projects/Ayta Mag Indi/{project_id}")
    save_path = Path(f"E:/Work/Pilot_projects/Ayta Mag Indi/simple_html")
    
    # Ensure the output directory exists
    os.makedirs(save_path, exist_ok=True)
    
    print(f"Will find html in {input_path} and save them to {save_path}")

    html_files = input_path.glob("*.htm")
    for html_file in html_files:
        simple_html_file = save_path / html_file.name
        if simple_html_file.is_file():
            continue
        else:
            print(f"Simplifying {html_file}")
        
        simple_html = simplify_html(html_file)

        # Write the simplified HTML to a new file
        with open(simple_html_file, 'w', encoding='utf-8') as f:
            f.write(simple_html)

if __name__ == "__main__":
    main()
