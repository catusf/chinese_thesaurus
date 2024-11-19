# Correcting the parse_explanation function to ensure accurate Pinyin extraction
import os
import json
from bs4 import BeautifulSoup

def parse_explanation_with_pinyin(headword, explanation):

    return {
        "headword": headword.strip(),
        "explanation": explanation.strip().replace("\n", " "),
    }

    pinyin = ""
    english_meanings = ""
    examples = ""
    
    # Split the explanation into segments
    parts = explanation.split("\n")
    if parts:
        # Pinyin is the second part before the square brackets
        if len(parts) > 0:
            first_line = parts[0]
            words = first_line.split()
            if len(words) > 1:
                pinyin = words[1]  # Extract the Pinyin
        # Extract English meanings enclosed in square brackets
        if "[" in explanation and "]" in explanation:
            english_start = explanation.index("[")
            english_end = explanation.index("]")
            english_meanings = explanation[english_start + 1:english_end].strip()
        # The rest is treated as examples
        examples = explanation.split("]")[-1].strip() if "]" in explanation else explanation.strip()

    return {
        "headword": headword.strip(),
        "pinyin": pinyin.strip(),
        "english": english_meanings.strip(),
        "examples": examples.strip()
    }

# Update the parsing function to use the corrected explanation parser
def parse_html_with_fixed_pinyin(file_path):
    print(f"Processing {file_path}...")

    html_content = None  # Initialize html_content to ensure it exists
    try:
        # Attempt to read with GBK encoding
        with open(file_path, "r", encoding="gbk", errors='ignore') as file:
            html_content = file.read()
    except UnicodeDecodeError:
        try:
            # Attempt to read with UTF-8 encoding
            with open(file_path, "r", encoding="utf-8") as file:
                html_content = file.read()
        except UnicodeDecodeError:
            try:
                # Attempt to read with GBK encoding, ignoring errors
                with open(file_path, "r", encoding="gbk", errors='ignore') as file:
                    html_content = file.read()
            except UnicodeDecodeError:
                print(f"*** Unicode error while reading {file_path}")
                return  # Exit if none of the encodings work

    finally:
        if html_content is None:
            print(f"Unable to process file: {file_path}")
                    
    if html_content is None:
        print(f"Failed to read content from {file_path}")
        return

    try:
        soup = BeautifulSoup(html_content, 'html.parser')
    except Exception as e:
        print(f"Error parsing HTML content from {file_path}: {e}")
        return

    # Continue with your processing logic...

    result = {
        "近义词": [],
        "反义词": [],
        "词典解释": []
    }

    for section in soup.find_all('div', class_='jsitem'):
        title = section.find('div', class_='title').get_text(strip=True)
        content = section.find('div', class_='content')
        if "近义词" in title:
            for row in content.find_all('tr'):
                cells = row.find_all('td')
                if cells:
                    headword = cells[0].get_text(strip=True)
                    explanation = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                    result["近义词"].append(parse_explanation_with_pinyin(headword, explanation))
        elif "反义词" in title:
            for row in content.find_all('tr'):
                cells = row.find_all('td')
                if cells:
                    headword = cells[0].get_text(strip=True)
                    explanation = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                    result["反义词"].append(parse_explanation_with_pinyin(headword, explanation))
        elif "词典解释" in title:
            explanation = content.get_text(strip=True)
            result["词典解释"].append(explanation)
    
    return result

def process_folder(folder_path, output_file):
    # Parse all uploaded HTML files and save results to JSON
    pinyin_fixed_data = {}
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".html"):  # Process only HTML files
            file_path = os.path.join(folder_path, file_name)
            pinyin_fixed_data[file_name] = parse_html_with_fixed_pinyin(file_path)

    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(pinyin_fixed_data, json_file, ensure_ascii=False, indent=4)

    # Save the results to a JSON file

# folder_path = r"data/details"  # Replace with the path to your folder
folder_path = r"C:\Sites\KXue\jyc.kxue.com\m\jinyici"  # Replace with the path to your folder
output_file = "output_details.json"  # Replace with your desired output file name
process_folder(folder_path, output_file)

