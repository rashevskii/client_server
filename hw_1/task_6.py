"""
    6. Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет»,
    «декоратор». Проверить кодировку файла по умолчанию. Принудительно открыть файл в формате Unicode и вывести его
    содержимое.
"""
import chardet

WORDS = ["сетевое программирование", "сокет", "декоратор"]
with open('test_file.txt', 'w') as f:
    for word in WORDS:
        f.write(f"{word}\n")

with open('test_file.txt', 'rb') as f:
    data = f.read()

encoding = chardet.detect(data)['encoding']
print(f'Кодировка текста по-молчанию: {encoding}')

with open('test_file.txt', 'r', encoding=encoding) as f:
    data = f.read()

print(f'Содержимое файла: {data}')