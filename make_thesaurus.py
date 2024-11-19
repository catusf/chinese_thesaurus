import json
import argparse
from collections import defaultdict
from pinyin import get as pinyinget

# Constants
MAX_ITEMS = 100000  # For debug purposes
BIG_ITEMS = 50  # For debug purposes

PC_NEWLINE = chr(0xEAB1)
PC_RIGHT_TRIANGLE = "»"  # ▸
PC_SEPERATOR_1 = " "
PC_SEPERATOR_2 = "、"

def pleco_make_bold(text):
    return f"{chr(0xEAB2)}{text}{chr(0xEAB3)}"

def pleco_make_link(text):
    return f"{chr(0xEAB8)}{text}{chr(0xEABB)}"

def make_linked_items(cur_item, list_items, include_pinyin=True):
    items = sorted(list(set(list_items)))  # Removes duplicated lines
    contents = ""

    for line in items:
        tokens = set(line.split(' '))
        tokens.discard(cur_item)

        words = [
            pleco_make_link(word) + (" " + pinyinget(word) if include_pinyin else "")
            for word in sorted(list(tokens))
        ]
        sep = PC_SEPERATOR_1 if include_pinyin else PC_SEPERATOR_2
        # print(f"Sep: {sep}")
        contents += f"{PC_RIGHT_TRIANGLE} {sep.join(words)}\n"

    return contents

def main():
    # Initialize argument parser
    parser = argparse.ArgumentParser(description="Process a thesaurus dictionary and generate output.")
    parser.add_argument("--no-pinyin", action="store_true", help="Exclude Pinyin from the generated output.")
    args = parser.parse_args()

    # Initialize the synonym dictionary with defaultdict
    thesaurus_dict = defaultdict(lambda: {
        "SynonymSet": [], "RelatedSet": [], "IndependentSet": [],
        "AntonymSet": [], "NegationSet": []
    })

    # Process thesaurus files
    with open('data/dict_synonym.txt', 'r', encoding='utf-8') as file:
        count = 0
        print(f"Reading dict_synonym.txt...")
        for line in file:
            line = line.strip()
            if not line:
                continue
            if count > MAX_ITEMS:
                break
            count += 1
            try:
                category, words = line.split(' ', 1)
            except ValueError:
                print(f"Invalid format line: {line}")
                continue

            type_char = category[-1]
            thesaurus_type = {
                '=': "SynonymSet",
                '#': "RelatedSet",
                '@': "IndependentSet"
            }.get(type_char, None)
            if not thesaurus_type:
                print(f"Incorrect line: {line}")
                continue

            word_list = words.split()
            for word in word_list:
                thesaurus_dict[word][thesaurus_type].append(words)

    with open('data/dict_antonym.txt', 'r', encoding='utf-8') as file:
        count = 0
        print(f"Reading dict_antonym.txt...")
        for line in file:
            line = line.strip()
            if not line:
                continue
            count += 1
            if count > MAX_ITEMS:
                break
            try:
                word1, word2 = line.split('-', 1)
            except ValueError:
                print(f"Invalid format line: {line}")
                continue

            thesaurus_dict[word1]["AntonymSet"].append(word2)
            thesaurus_dict[word2]["AntonymSet"].append(word1)

    ignore_negations = {'不', '没'}
    with open('data/dict_negative.txt', 'r', encoding='utf-8') as file:
        count = 0
        print(f"Reading dict_negative.txt...")
        negations = []
        for line in file:
            line = line.strip()
            if not line:
                continue
            count += 1
            if count > MAX_ITEMS:
                break
            try:
                word, _ = line.split('\t', 1)
            except ValueError:
                print(f"Invalid format line: {line}")
                continue
            negations.append(word)

        for word in thesaurus_dict:
            if word in ignore_negations:
                continue
            for negation in negations:
                if word in negation:
                    thesaurus_dict[word]["NegationSet"].append(negation)

    # Write JSON output
    with open('data/thesaurus_dict.json', 'w', encoding='utf-8') as json_file:
        json.dump(thesaurus_dict, json_file, ensure_ascii=False, indent=4)

    pleco_file = "data/SND-Pleco.txt"

    if args.no_pinyin:
        pleco_file = pleco_file.replace(".txt", "-no_pinyin.txt")

    # Generate Pleco dictionary
    with open(pleco_file, 'w', encoding='utf-8') as snd_file:
        count = 0
        print(f"Generating Pleco dict...")
        for item in thesaurus_dict:
            antonyms = set(thesaurus_dict[item]["AntonymSet"])
            synonyms = set(thesaurus_dict[item]["SynonymSet"])
            negations = set(thesaurus_dict[item]["NegationSet"])

            if not (len(antonyms) + len(synonyms) + len(negations)):
                continue

            count += 1
            if count > MAX_ITEMS:
                break

            contents = f'{item}\t{pinyinget(item)}\t'

            for thesaurus_type, label in [("AntonymSet", "ANTONYM"), ("SynonymSet", "SYNONYM"), ("NegationSet", "NEGATION")]:
                list_items = thesaurus_dict[item][thesaurus_type]
                if list_items:
                    contents += f"{pleco_make_bold(label)}\n"
                    contents += make_linked_items(item, list_items, include_pinyin=not args.no_pinyin)

            contents = contents.replace('\n', PC_NEWLINE)
            snd_file.write(f'{contents}\n')

        print(f"Created {count} items.")

if __name__ == "__main__":
    main()
