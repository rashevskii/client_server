"""
    4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления в
    байтовое и выполнить обратное преобразование (используя методы encode и decode).
"""

WORDS = ["разработка", "администрирование", "protocol", "standard"]


def encode_decode(arr):
    for word in arr:
        enc_word = word.encode('utf-8')
        print(f"Слово в байтах - {enc_word}")
        print(f"Слово после декодирования - {enc_word.decode('utf-8')}")


encode_decode(WORDS)
