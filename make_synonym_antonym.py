import json
from collections import defaultdict
from pinyin import get as pinyinget
from hanzipy.dictionary import HanziDictionary

# searcher = HanziDictionary()
# result = searcher.definition_lookup("好", script_type="simplified")


# print(result)

# Initialize the synonym dictionary with defaultdict
thesaurus_dict = defaultdict(lambda: {"SynonymSet": [], "RelatedSet": [], "IndependentSet": [], "AntonymSet": [], "NegateSet": []})

# Path to the uploaded file

MAX_ITEMS = 100000 # For debug purposes

BIG_ITEMS = 50 # For debug purposes

PC_NEWLINE = chr(0xEAB1)
PC_RIGHT_TRIANGLE = "▸"  # ▸

def pleco_make_bold(text):
    return f"{chr(0xEAB2)}{text}{chr(0xEAB3)}"

def pleco_make_link(text):
    return f"{chr(0xEAB8)}{text}{chr(0xEABB)}"

def make_linked_items(list_items):
    contents = f"{PC_RIGHT_TRIANGLE} "

    for line in list_items:
        words = line.split(' ')

        for word in words:
            contents += f"{pleco_make_link(word)} "

        contents += '\n'
    return contents

# Process the file line by line
with open('dict_synonym.txt', 'r', encoding='utf-8') as file:
    count = 0
    print(f"Reading dict_synonym.txt...")
    for line in file:        
        # Remove any trailing newline or spaces
        line = line.strip()
        if not line:
            continue
        
        if count > MAX_ITEMS:
            break
        
        count+=1

        # Split the line into Category and Words
        try:
            category, words = line.split(' ', 1)
        except ValueError:
            print(f"Invalid format line: {line}")
            continue

        # Determine the type from the last character of Category
        type_char = category[-1]
        thesaurus_type = (
            "SynonymSet" if type_char == '=' else
            "RelatedSet" if type_char == '#' else
            "IndependentSet" if type_char == '@' else None
        )
        if not thesaurus_type:
            print(f"Incorrect line: {line}")
            continue

        # Split the Words into individual words
        word_list = words.split()

        # Populate the dictionary
        for word in word_list:
            thesaurus_dict[word][thesaurus_type].append(words)
    
    print(f"Found {count} items.")

# Process the file line by line
with open('dict_antonym.txt', 'r', encoding='utf-8') as file:
    count = 0
    print(f"Reading dict_antonym.txt...")
    for line in file:
        line = line.strip()
        if not line:
            continue
        
        count+=1

        if count > MAX_ITEMS:
            break
        
        # Split the line into Category and Words
        try:
            word1, word2 = line.split('-', 1)
        except ValueError:
            print(f"Invalid format line: {line}")
            continue
            
        thesaurus_dict[word1]["AntonymSet"].append(word2)
        thesaurus_dict[word2]["AntonymSet"].append(word1)
    print(f"Found {count} items.")

ignore_negates = set(['不', '没'])

# Process the file line by line
with open('dict_negative.txt', 'r', encoding='utf-8') as file:
    count = 0
    print(f"Reading dict_negative.txt...")

    negates = []
    for line in file:
        line = line.strip()
        if not line:
            continue

        count += 1

        if count > MAX_ITEMS:
            break
        
        # Split the line into Category and Words
        try:
            word, _ = line.split('\t', 1)
        except ValueError:
            print(f"Invalid format line: {line}")
            continue
            
        negates.append(word)

    print(f"Found {count} items.")

    for word in thesaurus_dict:
        if word in ignore_negates: # Skips too frequently used ones
            continue

        for negate in negates:
            if word in negate:
                thesaurus_dict[word]["NegateSet"].append(negate)

# Serialize to JSON format
output_path = 'updated_synonym_dict.json'

with open(output_path, 'w', encoding='utf-8') as json_file:
    json.dump(thesaurus_dict, json_file, ensure_ascii=False, indent=4)

# Calculate and print the total number of items for all words
total_items_count = 0

SUB_KEYS = thesaurus_dict['好'].keys()
big_items = 0

with open(f'big_items-{BIG_ITEMS}.txt', 'w', encoding='utf-8') as big_file:
    for item in thesaurus_dict:
        total_items_count += len(thesaurus_dict[item].values())

        for sub in SUB_KEYS:
            for words in thesaurus_dict[item][sub]:
                if len(words) > BIG_ITEMS:
                    # print(f"{item} > {sub}")
                    big_file.write(f"{item} > {sub} > {words}\n")
                    big_items+=1

print(f"Big items: {big_items}")

print(f"Dict items count: {len(thesaurus_dict)}")

print(f"Total number of items across all words: {total_items_count}")

print(f"Updated synonym dictionary saved to: {output_path}")

with open('SND-Pleco.txt', 'w', encoding='utf-8') as snd_file:
    count = 0
    print(f"Generating Pleco dict...")
    contents = ''

    for item in thesaurus_dict:
        count += 1

        if count > MAX_ITEMS:
            break

        contents = f'{item}\t{pinyinget(item)}\t'

        list_items = thesaurus_dict[item]["AntonymSet"]
        if list_items:
            contents += f"{pleco_make_bold('ANTONYM')}\n"

            contents += make_linked_items(list_items)

        list_items = thesaurus_dict[item]["SynonymSet"]
        if list_items:
            contents += f"{pleco_make_bold('SYNONYM')}\n"
            
            contents += make_linked_items(list_items)

        list_items = thesaurus_dict[item]["NegateSet"]
        if list_items:
            contents += f"{pleco_make_bold('NEGATE')}\n"

            contents += make_linked_items(list_items)

        contents = contents.replace('\n', PC_NEWLINE)

        snd_file.write(f'{contents}\n')

    print(f"Created {count} items.")
