import string
import random

import requests


url_list = [
    "https://github.com/",
    "https://ru.wikipedia.org/wiki/%D0%97%D0%B0%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0"
]


def create_random_string(length: int):
    """
    Создает рандомную строку.
    :param length: длина строки.
    :return: строка размером с length.
    """
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))


def get_and_save(urls: list):
    """
    Получить коды страниц и сохранить.
    :param urls: Список url страниц
    """
    for url in urls:
        try:
            resp = requests.get(url)
            with open(f"{create_random_string(6)}.html", 'wb') as file_data:
                file_data.write(resp.content)
        except Exception as e:
            print(f"Ошибка обработки страницы - {e}")


get_and_save(url_list)
