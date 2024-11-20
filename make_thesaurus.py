import json
import argparse
from collections import defaultdict
from pinyin import get as pinyinget
import re

from dragonmapper.transcriptions import numbered_to_accented

from pycccedict.cccedict import CcCedict

from chin_dict.chindict import ChinDict
cd = ChinDict()

lookups = {}

cccedict = CcCedict()
# Constants
MAX_ITEMS = 5000  # For debug purposes
BIG_ITEMS = 50  # For debug purposes

PC_NEWLINE = chr(0xEAB1)
PC_RIGHT_TRIANGLE = "»"  # ▸
PC_SEPARATOR_1 = " "
PC_SEPARATOR_2 = "、"
PC_MIDDLE_DOT = "·"


import time

class Timer:
    """
    A Timer class to measure elapsed time with start, stop, and display functionalities.
    """
    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        """Start the timer."""
        self.start_time = time.time()
        self.end_time = None
        print("Timer started.")

    def stop(self):
        """Stop the timer."""
        if self.start_time is None:
            raise ValueError("Timer has not been started.")
        self.end_time = time.time()
        print("Timer stopped.")

    def elapsed_time(self):
        """Calculate and return the elapsed time in minutes, seconds, and milliseconds."""
        if self.start_time is None:
            raise ValueError("Timer has not been started.")
        if self.end_time is None:
            raise ValueError("Timer has not been stopped.")

        elapsed_time = self.end_time - self.start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        milliseconds = int((elapsed_time * 1000) % 1000)

        return {
            'minutes': minutes,
            'seconds': seconds,
            'milliseconds': milliseconds
        }

    def display_elapsed(self):
        """Display the elapsed time."""
        elapsed = self.elapsed_time()
        print(f"Elapsed time: {elapsed['minutes']}:{elapsed['seconds']}.{elapsed['milliseconds']}s")


def remove_spaces(text):
    return text.replace(" ", "")

def convert_to_mark_pinyin(text):
    # Define the regex as a constant
    BRACKETS_REGEX = r'\[([^\]]+)\]'
    
    # Function to convert matched text to uppercase
    def replace_with_uppercase(match):
        return f"[{numbered_to_accented(match.group(1))}]"
        
    return re.sub(BRACKETS_REGEX, replace_with_uppercase, text)

def circled_number(n):
    """ Returns circled numbers, maxes out at 35
    """
    if 1 <= n <= 20:
        return chr(9311 + n)  # Unicode offset for circled digits ① to ⑳
    elif 21 <= n <= 35:  # Circled numbers 21–35
        return chr(12881 + n - 20)  # Unicode offset for Ⓐ-Ⓙ and beyond
    else:
        return str(n)  # Fallback to normal numbers
    
def pleco_make_italic(text):
    return f"{chr(0xEAB4)}{text}{chr(0xEAB5)}"

def pleco_make_bold(text):
    return f"{chr(0xEAB2)}{text}{chr(0xEAB3)}"

def pleco_make_link(text):
    return f"{chr(0xEAB8)}{text}{chr(0xEABB)}"

DEF_SEPERATOR = "/"
def get_def_contens(item, has_marker=True):
    definitions = None
    try:
        if item in lookups:
            definitions = lookups[item]
        else: 
            definitions = cd.lookup_word(item)
            lookups[item] = definitions
    except Exception as e:
        # print(f"Error looking up word '{item}': {e}")
        return "\n"

    contents = ""
    if has_marker:
        contents += f"{pleco_make_bold("DEFINITION")}\n"

    for definition in definitions:
        dict_pinyin = remove_spaces(numbered_to_accented(definition.pinyin))
        # if remove_spaces(dict_pinyin) != remove_spaces(pinyin):
        contents += f"{pleco_make_italic(dict_pinyin)} "

        contents += f"{"; ".join([convert_to_mark_pinyin(item.strip()) for item in definition.meaning])}{DEF_SEPERATOR}"
    
    if contents[-1] == DEF_SEPERATOR:
        contents = contents[:-1]
    
    contents += "\n"

    return contents

def make_linked_items(cur_item, list_items, include_pinyin=True, add_definitions=False):
    items = sorted(list(set(list_items)))  # Removes duplicated lines
    contents = ""

    for line in items:
        tokens = set(line.split(' '))
        tokens.discard(cur_item)

        words = []

        for item in tokens:
            if add_definitions:
                word = pleco_make_link(item) + " " + get_def_contens(item, has_marker=False)

            else:
                word = pleco_make_link(item) + (" " + pinyinget(item) if include_pinyin else "")

            words.append(word)

        sep = PC_SEPARATOR_1 if include_pinyin else PC_SEPARATOR_2
        # print(f"Sep: {sep}")
        contents += f"{PC_RIGHT_TRIANGLE} {sep.join(words)}\n"

    return contents

def main():
    # Initialize argument parser
    parser = argparse.ArgumentParser(description="Process a thesaurus dictionary and generate output.")
    parser.add_argument("--no-pinyin", default=False, action="store_true", help="Exclude Pinyin from the generated output.")
    parser.add_argument("--add-definition", default=True, action="store_true", help="Exclude Pinyin from the generated output.")
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
            definitions = None
            if args.add_definition:
                try:
                    definitions = cd.lookup_word(item)
                except:
                    # print(f"No results for word: '{item}")
                    pass

            pinyin = pinyinget(item)
            contents = f'{item}\t{pinyin}\t'

            if definitions:
                contents += f"{pleco_make_bold("DEFINITION")}\n"

                for definition in definitions:
                    dict_pinyin = remove_spaces(numbered_to_accented(definition.pinyin))
                    if remove_spaces(dict_pinyin) != remove_spaces(pinyin):
                         contents += f"{pleco_make_italic(dict_pinyin)} "

                    contents += f"{"; ".join(definition.meaning)}\n"

            for thesaurus_type, label in [("AntonymSet", "ANTONYM"), ("SynonymSet", "SYNONYM"), ("NegationSet", "NEGATION")]:
                list_items = thesaurus_dict[item][thesaurus_type]
                if list_items:
                    contents += f"{pleco_make_bold(label)}\n"
                    contents += make_linked_items(item, list_items, include_pinyin=not args.no_pinyin, add_definitions=args.add_definition)

            contents = contents.replace('\n', PC_NEWLINE)
            snd_file.write(f'{contents}\n')

        print(f"Created {count} items.")

if __name__ == "__main__":
    timer = Timer()
    timer.start()
    main()
    timer.stop()
    timer.display_elapsed()
