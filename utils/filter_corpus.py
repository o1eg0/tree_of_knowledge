import enchant
from nltk.tokenize import word_tokenize

# Создаем объект словаря для английского языка
d = enchant.Dict("en_US")


def filter_english_words(text):
    # Токенизация исходного текста
    tokens = word_tokenize(text)

    # Фильтрация слов, проверка на присутствие в английском языке
    filtered_words = [word for word in tokens if d.check(word) or d.check(word.capitalize())]

    # Возврат отфильтрованного текста
    return ' '.join(filtered_words)
