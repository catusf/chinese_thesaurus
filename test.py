
# from pinyin import get as pinyinget

# from pinyin_jyutping_sentence import pinyin as spinyin

# text = "行旅。他是来自美国的Steven，现在在中国旅行"

# print(f"By pinyin: {pinyinget(text)}")

# print(f"By pinyin_jyutping_sentence: {spinyin(text)}")

from chin_dict.chindict import ChinDict

import json


def wordresult_to_dic(wordresult):
    results = []

    for item in wordresult:
        results.append({"meaning": item.meaning, 
                        "pinyin": item.pinyin, 
                        "simplified": item.simplified, 
                        "traditional": item.traditional})
    return results

cd = ChinDict()
item = "人"

LOOKUPS_FILE = "lookups.json"

# Load lookups from a JSON file
try:
    with open(LOOKUPS_FILE, "r", encoding="utf-8") as f:
        lookups = json.load(f)
except FileNotFoundError:
    lookups = {}

def save_lookups():
    """Save the lookups dictionary to a JSON file."""
    with open(LOOKUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(lookups, f, ensure_ascii=False, indent=4)


definitions = None
try:
    if item in lookups:
        definitions = lookups[item]
        print(f"Uses cached {lookups}")
    else: 
        definitions = wordresult_to_dic(cd.lookup_word(item))
        lookups[item] = definitions
        print(f"New search")
except Exception as e:
    print(f"Error looking up word '{item}': {e}")
    # return f"\n"

print(definitions)

save_lookups()