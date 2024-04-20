from coptic.coptic import coptic_processing
from data_collection.sort_books import sort_books
from data_conversion.convert_pdf_eng_to_text import convert_pdf_eng_books_to_text
from graphs_construction.graphs_building import build_graphs
from text_processing.reduce_noise_and_preprocess import reduce_noise_and_preprocess
from utils.find_yadisk_files import get_yadisk_client

email = 'oleg36531@gmail.com'
token = 'Invalid token'

if __name__ == '__main__':
    print('Добро пожаловать в Tree of knowledge')
    client = get_yadisk_client(email, token)

    # Этам обработки коптского языка
    ans = input('[Шаг 1] Вы хотите начать обработку коптского языка? [y/N] ')
    if ans.lower() == 'y':
        coptic_processing()

    # Этап сортировки полученных данных
    ans = input('[Шаг 2] Вы хотите начать катологизацию книг? Это может занять много времени [y/N] ')
    if ans.lower() == 'y':
        sort_books(client)

    # Этап конвертации файлов
    ans = input('[Шаг 3] Вы хотите начать конвертацию англоязычных книг из PDF? Это может занять много времени [y/N] ')
    if ans.lower() == 'y':
        convert_pdf_eng_books_to_text(client)

    # Этап очищения от шума
    ans = input('[Шаг 4] Вы хотите начать препроцессинг англоязычных текстов? [y/N] ')
    if ans.lower() == 'y':
        reduce_noise_and_preprocess(client)

    # Этап построения графа n-грамм и семантической сети
    ans = input('[Шаг 4] Вы хотите начать посроение графов на основе корпуса? [y/N] ')
    if ans.lower() == 'y':
        build_graphs()

    print('Выполнение программы завершено')
