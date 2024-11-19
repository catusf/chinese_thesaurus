import json
from collections import defaultdict
from pinyin import get as pinyinget
# from hanzipy.dictionary import HanziDictionary

# searcher = HanziDictionary()
# result = searcher.definition_lookup("好", script_type="simplified")
# print(result)

# Initialize the synonym dictionary with defaultdict
thesaurus_dict = defaultdict(lambda: {"SynonymSet": [], "RelatedSet": [], "IndependentSet": [], "AntonymSet": [], "NegationSet": []})

meaning_dict = {}

# Path to the uploaded file

MAX_ITEMS = 100000 # For debug purposes

BIG_ITEMS = 50 # For debug purposes

PC_NEWLINE = chr(0xEAB1)
PC_RIGHT_TRIANGLE = "»"  # ▸

def pleco_make_bold(text):
    return f"{chr(0xEAB2)}{text}{chr(0xEAB3)}"

def pleco_make_link(text):
    return f"{chr(0xEAB8)}{text}{chr(0xEABB)}"

def make_linked_items(cur_item, list_items):
    items = sorted(list(set(list_items))) # Removes duplicated lines 
    contents = ""

    for line in items:
        tokens = set(line.split(' '))
        tokens.discard(cur_item)
        
        words = [(pleco_make_link(word) + " " + pinyinget(word)) for word in sorted(list(tokens))]
        contents += f"{PC_RIGHT_TRIANGLE} {" ".join(words)}\n"
    
    return contents

import json

thesaurus_dict = defaultdict(lambda: {"SynonymSet": [], "RelatedSet": [], "IndependentSet": [], "AntonymSet": [], "NegationSet": []})

sym_list_path = "output_list.json"
sym_details_path = "output_details.json"

# Open and load the JSON file
# with open(sym_list_path, 'r', encoding='utf-8') as file:
#     items = json.load(file)

#     for item in items:
#         word = item['Word']
#         words_text = item['Synonyms']
#         words = words_text.split('、')
        
#         # Populate the dictionary
#         # for word in syns:
#         #     thesaurus_dict[word][thesaurus_type].append(words)
        
#         thesaurus_dict[word]["SynonymSet"].append(words_text)

#         pass

with open(sym_details_path, 'r', encoding='utf-8') as file:
    items = json.load(file)

    for key in items:
        item = items[key]
        word = item['单词']
        synonyms = item['近义词']
        antonyms = item["反义词"]
        meanings = item["词典解释"] 
        
        # Populate the dictionary
        # for word in syns:
        #     thesaurus_dict[word][thesaurus_type].append(words)
        
        # thesaurus_dict[word]["SynonymSet"].append(words_text)

        pass

# Print the loaded data

