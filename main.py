import yadisk


def get_yadisk_client():
    global email, token
    while True:
        token = input(f'Пожалуйста, укажите ваш yadisk токен, если у вас его нет, обратитесь к {email}\n')
        try:
            yadisk_client = yadisk.Client(token=token)
            if yadisk_client.check_token():
                return yadisk_client
        except Exception as e:
            pass
        print('Некорректный токен!')


def ask_coptic_processing():
    ans = input('[Шаг 1] Вы хотите начать обработку коптского языка? [y/N]')
    if ans.lower() != 'y':
        return
    # coptic_processing()


def ask_sort_books(y):
    ans = input('[Шаг 2] Вы хотите начать катологизацию книг? [y/N]')
    if ans.lower() != 'y':
        return
    # sort_books(y)


def ask_convert_pdf_eng_books_to_text(y):
    ans = input('[Шаг 3] Вы хотите начать конвертацию англоязычных книг из PDF в текст? [y/N] ')
    if ans.lower() != 'y':
        return
    # convert_pdf_eng_books_to_text(y)


def ask_reduce_noise_and_preprocess(y):
    ans = input('[Шаг 4] Вы хотите начать препроцессинг англоязычных текстов? [y/N] ')
    if ans.lower() != 'y':
        return
    # reduce_noise_and_preprocess(y)


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
token = 'invalid'

if __name__ == '__main__':
    print('Добро пожаловать в Tree of knowledge')
    client = get_yadisk_client()

    ask_coptic_processing()
    ask_sort_books(client)
    ask_convert_pdf_eng_books_to_text(client)
    ask_reduce_noise_and_preprocess(client)
    ask_build_graphs()
    ask_visualize_graphs()
    print('Выполнение программы завершено')
