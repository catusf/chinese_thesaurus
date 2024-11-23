import json
import argparse
from collections import defaultdict
#from pinyin import get as pinyinget
from pinyin_jyutping_sentence import pinyin as pinyinget
import re
import time
import io

from dragonmapper.transcriptions import numbered_to_accented

from pycccedict.cccedict import CcCedict

from chin_dict.chindict import ChinDict
import json
import json
from chin_dict.chindict import ChinDict


class ChineseDictionary:
    def __init__(self, lookups_file="lookups.json"):
        """
        Initialize the ChineseDictionary class with an optional path to the lookups file.
        """
        self.cd = ChinDict()
        self.lookups_file = lookups_file
        self.lookups = self.load_lookups()

    @staticmethod
    def wordresult_to_dic(wordresult):
        """
        Convert word lookup results to a dictionary format.
        """
        results = []
        for item in wordresult:
            results.append({
                "meaning": item.meaning,
                "pinyin": item.pinyin,
                "simplified": item.simplified,
                "traditional": item.traditional
            })
        return results

    def load_lookups(self):
        """
        Load lookups from a JSON file. Return an empty dictionary if the file doesn't exist.
        """
        try:
            with open(self.lookups_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_lookups(self):
        """
        Save the current lookups dictionary to a JSON file.
        """
        with io.open(self.lookups_file, "w", encoding="utf-8") as f:
            json.dump(self.lookups, f, ensure_ascii=False, indent=4)

    def lookup(self, word):
        """
        Look up a word and return its definitions. Cache the results in the lookups dictionary.
        """
        definitions = None
        try:
            if word in self.lookups:
                print(f"Using cached result for '{word}'")
                return self.lookups[word]
            else:
                print(f"Performing new search for '{word}'")
                definitions = self.wordresult_to_dic(self.cd.lookup_word(word))
        except Exception as e:
            print(f"Error looking up word '{word}': {e}")

        self.lookups[word] = definitions
        return definitions

    def __del__(self):
        """
        Ensure lookups are saved when the object is destroyed.
        """
        self.save_lookups()



cccedict = CcCedict()
# Constants
BIG_ITEMS = 50  # For debug purposes

PC_NEWLINE = chr(0xEAB1)
PC_RIGHT_TRIANGLE = "»"  # ▸
PC_SEPARATOR_1 = " "
PC_SEPARATOR_2 = "、"
PC_MIDDLE_DOT = "·"

def remove_chinese_with_pipe(text):
    """
    Remove the Traditional Chinese characters before the '|' and the '|' itself in the input string.
    
    Args:
        text (str): The input text to be cleaned.
        
    Returns:
        str: The cleaned text.
    """
    return re.sub(r'[\u4e00-\u9fff]+\|', '', text)

def convert_to_mark_pinyin(text):
    # Define the regex as a constant
    BRACKETS_REGEX = r'(\[[^\]]+\])'
    
    # Function to convert matched text to uppercase
    def replace_with_uppercase(match):
        # return match.group(1)
        return f" {numbered_to_accented(match.group(1))[1:-1]}"
        
    return re.sub(BRACKETS_REGEX, replace_with_uppercase, text)
    
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


def circled_number(n):
    """ Returns circled numbers, maxes out at 35
    """
    if 1 <= n <= 20:
        return chr(9311 + n)  # Unicode offset for circled digits ① to ⑳
    elif 21 <= n <= 35:  # Circled numbers 21–35
        return chr(12881 + n - 20)  # Unicode offset for Ⓐ-Ⓙ and beyond
    else:
        return str(n)  # Fallback to normal numbers

def pleco_make_dark_gray(text):  # Light Slate Gray
    return f"{text}"
    
def pleco_make_italic(text):
    return f"{chr(0xEAB4)}{text}{chr(0xEAB5)}"

def pleco_make_bold(text):
    return f"{chr(0xEAB2)}{text}{chr(0xEAB3)}"

def pleco_make_link(text):
    return f"{chr(0xEAB8)}{text}{chr(0xEABB)}"

DEF_SEPERATOR = "/"

dictionary = ChineseDictionary()


def get_def_contents(item, dict_size, has_marker=False):
    definitions = dictionary.lookup(item)

    if not definitions:
        return f"{pleco_make_italic(pinyinget(item))}\n" if dict_size in ["mid", "big"] else "\n"

    contents = ""
    if has_marker:
        contents += f"{pleco_make_bold("DEFINITION")}\n"

    for definition in definitions:
        if dict_size in ["mid", "big"]: # Adds Pinyin
            contents += f"{pleco_make_italic(numbered_to_accented(definition["pinyin"]).replace(" ", ""))} "

        contents += f"{"; ".join([remove_chinese_with_pipe(convert_to_mark_pinyin(item.strip())) for item in definition["meaning"]])}{DEF_SEPERATOR}"
    
    if contents[-1] == DEF_SEPERATOR:
        contents = contents[:-1]
    
    contents += "\n"

    return contents

def make_linked_items(cur_item, lines, dict_size):
    # lines = sorted(list(set(list_items)))  # Removes duplicated lines
    contents = ""

    for index, line in enumerate(lines, start=1):
        tokens = set(line.split(' '))
        tokens.discard(cur_item) # Dont repeat the headword
        tokens = sorted(list(tokens))

        words = []

        for token in tokens:
            if dict_size in ["big"]:
                word = pleco_make_link(token) + " " + get_def_contents(token, dict_size=dict_size, has_marker=False)

            else:
                word = pleco_make_link(token) + (" " + pinyinget(token) if dict_size in ["mid", "big"] else "")

            words.append(word)

        sep = PC_SEPARATOR_1 if dict_size in ["mid", "big"] else PC_SEPARATOR_2

        contents += f"{circled_number(index)} {sep.join(words)}\n"

    return contents

def main():
    # Initialize argument parser
    parser = argparse.ArgumentParser(description="Process a thesaurus dictionary and generate output.")
    # parser.add_argument("--no-pinyin", default=False, action="store_true", help="Exclude Pinyin from the generated output.")
    # parser.add_argument("--add-definition", default=True, action="store_true", help="Exclude Pinyin from the generated output.")
    parser.add_argument("--dict-size", choices=['small', 'mid', 'big'], default="small", required=False,
                        help="Dictionary size: 'small' for Chinese thesaurus only, 'mid' adds Pinyin, 'big' adds definitions for words.")
    parser.add_argument("--num-items", type=int, default=1000000, required=False,
                        help="Maximum number of items to process (default: MAX_ITEMS).")
    args = parser.parse_args()

    # Use the --num-items argument to limit processing
    max_items = args.num_items
    dict_size = args.dict_size

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
            if count > max_items:
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
            if count > max_items:
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
            if count > max_items:
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

    pleco_file = "data/ChineseThesaurus-Pleco.txt"

    pleco_file = pleco_file.replace(".txt", f"-{dict_size}.txt")

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
            if count > max_items:
                break

            pinyin = pinyinget(item)
            contents = f'{item}\t\t'

            contents += get_def_contents(item, dict_size=dict_size, has_marker=False)

            for thesaurus_type, label in [("AntonymSet", "ANTONYM"), ("SynonymSet", "SYNONYM"), ("NegationSet", "NEGATION")]:
                list_items = sorted(list(set(thesaurus_dict[item][thesaurus_type]))) # Remove duplicated
                if list_items:
                    contents += f"{pleco_make_dark_gray(pleco_make_bold(label))}\n"
                    contents += make_linked_items(item, list_items, dict_size=dict_size)

            contents = contents.replace('\n', PC_NEWLINE)
            snd_file.write(f'{contents}\n')

        print(f"Created {count} items and saved to {pleco_file}")
    
    dictionary.save_lookups()

if __name__ == "__main__":
    timer = Timer()
    timer.start()
    main()
    timer.stop()
    timer.display_elapsed()
