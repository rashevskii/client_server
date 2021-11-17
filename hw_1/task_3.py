"""
    3. Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.
"""

WORDS = ["attribute", "класс", "функция", "type"]


def check_word(arr):
    for word in arr:
        for char in word:
            if ord(char) > 127:
                print(f"Слово '{word}' нельзя записать в байтовом типе")
                break


check_word(WORDS)
