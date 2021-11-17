"""
    2. Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в последовательность
    кодов (не используя методы encode и decode) и определить тип, содержимое и длину соответствующих переменных.
"""

WORDS = ["class", "function", "method"]
words_bytes = []


def encode_in_bytes(arr):
    for el in arr:
        words_bytes.append(eval(f"b'{el}'"))


def show_data(arr):
    for i in range(len(arr)):
        print(f"Элемент {i + 1} - {arr[i]}, тип - {type(arr[i])}, длина - {len(arr[i])}")


encode_in_bytes(WORDS)
show_data(words_bytes)
