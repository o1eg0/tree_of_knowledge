import logging
import os
import os.path

from tqdm import tqdm
from yadisk import Client

from utils import find_files


def create_corpus(y: Client, processed):
    files = []
    find_files(y, processed, files)

    corpus_filename = 'corpus.txt'
    filename = 'corpus.fragment'
    corpus = []
    for path in tqdm(files):
        try:
            y.download(path, filename)
            with open(filename,'r', encoding='utf-8') as file:
                text = file.read()

                if len(text) == 0:
                    logging.warning(f'{path} пуст')
                    continue

                corpus.append(text.replace('\n', ' '))
        except Exception as e:
            logging.error(e)

    with open(corpus_filename, 'w', encoding='utf-8') as file:
        file.write('\n'.join(corpus))

    if os.path.exists(filename):
        os.remove(filename)

    y.upload(corpus_filename, corpus_filename)
