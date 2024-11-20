import re
from pinyin_tone_converter.pinyin_tone_converter import PinyinToneConverter
from pycccedict.cccedict import CcCedict
from chin_dict.chindict import ChinDict

cd = ChinDict()
cccedict = CcCedict()
entry = cccedict.get_entry('好')

print(entry)

converter = PinyinToneConverter()
print(converter.convert_text(entry["pinyin"]))

def convert_to_mark_pinyin(text):
    # Define the regex as a constant
    BRACKETS_REGEX = r'\[([^\]]+)\]'
    
    # Function to convert matched text to uppercase
    def replace_with_uppercase(match):
        return f"[{converter.convert_text(match.group(1))}]"
        
    return re.sub(BRACKETS_REGEX, replace_with_uppercase, text)
        
text = 'used in 貓腰|猫腰[mao2yao1] and 鳥[bird]'

# Replace all occurrences
updated_text = convert_to_mark_pinyin("; ".join(entry["definitions"]))

print(updated_text)

print(cccedict.get_data_days_old())


# Call the function
days = 10


def circled_number(n):
    """ Returns circled numbers, maxes out at 35
    """
    if 1 <= n <= 20:
        return chr(9311 + n)  # Unicode offset for circled digits ① to ⑳
    elif 21 <= n <= 35:  # Circled numbers 21–35
        return chr(12881 + n - 20)  # Unicode offset for Ⓐ-Ⓙ and beyond
    else:
        return str(n)  # Fallback to normal numbers

print(entry["definitions"])
print("; ".join([f"{circled_number(index)} {text.strip()}" for index, text in enumerate(entry["definitions"], start=1)]))
print("\n".join([f"{circled_number(index)} {text.strip()}" for index, text in enumerate(entry["definitions"], start=1)]))
print("; ".join([f"{convert_to_mark_pinyin(text.strip())}" for index, text in enumerate(entry["definitions"], start=1)]))

headword = "好"
word_result = cd.lookup_word(headword)

print(f"Translations for {headword}:")
print("\n".join([word_result]))