import logging
import os
import os.path

import enchant
from nltk.tokenize import word_tokenize
from tqdm import tqdm
from yadisk import Client

from utils import find_files

coef_of_useless = 0.2
d = enchant.Dict("en_US")


def filter_english_words(text):
    texts = text.split('\n')
    answer = []
    for line in tqdm(texts, desc='Фильтр текстов'):
        if line.count(' ') / len(line) > coef_of_useless:
            continue

        tokens = word_tokenize(line)

        filtered_words = []
        for word in tokens:
            if d.check(word) or d.check(word.capitalize()):
                filtered_words.append(word)

        answer.append(' '.join(filtered_words))
    return '\n'.join(answer)


def create_corpus(y: Client, processed):
    files = []
    find_files(y, processed, files)

    corpus_filename = 'corpus.txt'

    filename = 'corpus.fragment'
    corpus = []
    for path in tqdm(files):
        try:
            y.download(path, filename)
            with open(filename, 'r', encoding='utf-8') as file:
                text = file.read()

                if len(text) == 0:
                    logging.warning(f'{path} пуст')
                    continue

                corpus.append(text.replace('\n', ' '))
        except Exception as e:
            logging.error(e)

    with open(corpus_filename, 'w', encoding='utf-8') as file:
        file.write(filter_english_words('\n'.join(corpus)))

    if os.path.exists(filename):
        os.remove(filename)

    y.upload(corpus_filename, corpus_filename)
