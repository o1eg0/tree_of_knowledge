import logging

import yadisk

from coptic.coptic import coptic_processing
from data_collection.sort_books import sort_books
from data_conversion.convert_pdf_eng_to_text import convert_pdf_eng_books_to_text
from text_processing.reduce_noise_and_preprocess import reduce_noise_and_preprocess


def get_yadisk_client():
    global email, token
    yadisk_client = yadisk.Client(token=token, default_args={'timeout': 300.0})
    if yadisk_client.check_token():
        return yadisk_client
    while True:
        token = input(f'Пожалуйста, укажите ваш yadisk токен, если у вас его нет, обратитесь к {email}\n')
        try:
            # Создаем экземпляр Yandex.Disk API
            yadisk_client = yadisk.Client(token=token, default_args={'timeout': 300.0})
            if yadisk_client.check_token():
                return yadisk_client
        except Exception as e:
            pass
        print('Некорректный токен!')


def ask_coptic_processing():
    ans = input('[Шаг 1] Вы хотите начать обработку коптского языка? [y/N] ')
    if ans.lower() != 'y':
        return
    coptic_processing()


def ask_sort_books(y):
    ans = input('[Шаг 2] Вы хотите начать катологизацию книг? Это может занять много времени [y/N] ')
    if ans.lower() != 'y':
        return
    sort_books(y)


def ask_convert_pdf_eng_books_to_text(y):
    ans = input('[Шаг 3] Вы хотите начать конвертацию англоязычных книг из PDF в текст? Это может занять много времени [y/N] ')
    if ans.lower() != 'y':
        return
    convert_pdf_eng_books_to_text(y)


def ask_reduce_noise_and_preprocess(y):
    ans = input('[Шаг 4] Вы хотите начать препроцессинг англоязычных текстов? [y/N] ')
    if ans.lower() != 'y':
        return
    reduce_noise_and_preprocess(y)


def ask_build_graphs():
    ans = input('[Шаг 5] Вы хотите построить графы на основе предобработанных англоязычных текстов? [y/N] ')
    if ans.lower() != 'y':
        return
    # build_graphs(y)


def ask_visualize_graphs():
    ans = input('[Шаг 6] Вы хотите визуализировать полученные графы? [y/N] ')
    if ans.lower() != 'y':
        return
    # visualize_graphs()


email = 'oleg36531@gmail.com'
token = 'y0_AgAEA7qkP__dAAt8WQAAAAD--L1jAABFLYpkSHxDt5jWLwyjjKUSbFdgVQ'

if __name__ == '__main__':
    print('Добро пожаловать в Tree of knowledge')
    client = get_yadisk_client()

    ask_coptic_processing()
    ask_sort_books(client)
    ask_convert_pdf_eng_books_to_text(client)
    ask_reduce_noise_and_preprocess(client)
    # ask_build_graphs()
    # ask_visualize_graphs()
    print('Выполнение программы завершено')
