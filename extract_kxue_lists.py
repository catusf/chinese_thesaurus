import os
from bs4 import BeautifulSoup
import pandas as pd
import json

def extract_data_from_html(file_path):
    try:
        # Attempt to read with UTF-8 encoding
        with open(file_path, "r", encoding="gbk", errors='ignore') as file:
            html_content = file.read()
    except UnicodeDecodeError:
        print(f'Unknown error occur: {file_path}')
            
    soup = BeautifulSoup(html_content, "html.parser")
    data = []
    table_rows = soup.select(".licontent")  # Select rows containing the desired data

    for row in table_rows:
        word = row.select_one(".hz a")  # First column (word)
        synonyms = row.select_one(".js")  # Second column (synonyms)
        if word and synonyms:
            data.append({"Word": word.text.strip(), "Synonyms": synonyms.text.strip()})

    return data

def process_folder(folder_path, output_file):
    all_data = {}
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".html"):  # Process only HTML files
            file_path = os.path.join(folder_path, file_name)
            extracted_data = extract_data_from_html(file_path)
            all_data[file_name] = extracted_data

    # Save all extracted data to a JSON file
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(all_data, json_file, ensure_ascii=False, indent=4)

# Example usage
folder_path = r"C:\Sites\KXue\jyc.kxue.com\m\list"  # Replace with the path to your folder
folder_path = r"data/list"  # Replace with the path to your folder
output_file = "output_list.json"  # Replace with your desired output file name
process_folder(folder_path, output_file)

print(f"Data extracted and saved to {output_file}")
