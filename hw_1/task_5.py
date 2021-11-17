"""
    5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из байтовового в строковый тип
    на кириллице.
"""

import subprocess
import chardet
import platform

RESOURCES = ['yandex.ru', 'youtube.com']


def ping_it(arr):
    count = "-n" if platform == 'Windows' else "-c"
    for el in arr:
        command = ["ping", count, "4", el]
        ping_output = subprocess.Popen(command, stdout=subprocess.PIPE)
        print(f"Result for {el}")
        for line in ping_output.stdout:
            result = chardet.detect(line)
            line = line.decode(result['encoding']).encode('utf-8')
            print(line.decode('utf-8')[:-1])


ping_it(RESOURCES)
