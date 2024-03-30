from pathlib import Path

from coptic.preprocessing import find_and_process_files, make_corpus
from coptic.word2vec import svd_dict_from_corpus, cbow_dict_from_corpus
from utils.npy_dict_to_excel import convert_npy_dict_to_xlsx

# Части речи, которые мы будем сохранять при обработке
PARTS_OF_SPEECH = [
    'NOUN',  # Существительные
    'VERB',  # Глаголы
    'ADJ',  # Прилагательные
    'ADV',  # Наречия
    'PRON',  # Местоимения
    'ADP',  # Предлоги
    'CONJ,'  # Союзы
    'CCONJ',  # Союзы
]

# Словарь собственных частей речи, которые мы будем заменять
PART_OF_REPLACE = {
    'PROPN': 'person1',
    'PER': 'person1',
    'PRON': 'pron1',
    'NUM': 'ordinal1'
}


def coptic_processing(
        home='./coptic',
        source_directory='{}/static/corpora',
        processed_directory='{}/static/processed_texts',
        corpus_path='{}/static/corpus.txt',
        svd_dict_path='{}/word2vec/svd/content/SVD_dictionary.npy',
        svd_directory='{}/word2vec/svd/content',
        cbow_save_path='{}/word2vec/cbow/content/CBOW_dictionary.npy'
):
    source_directory = source_directory.format(home)
    processed_directory = processed_directory.format(home)
    corpus_path = corpus_path.format(home)
    svd_dict_path = svd_dict_path.format(home)
    svd_directory = svd_directory.format(home)
    cbow_save_path = cbow_save_path.format(home)

    print(f'Директория с копсткими файлами: {Path(source_directory).absolute()}')
    print(f'Директория с предобработанными файлами: {Path(processed_directory).absolute()}')
    print(f'Файл с корпусом текстов: {Path(corpus_path).absolute()}')
    print(f'Файл с SVD словарем: {Path(svd_dict_path).absolute()}')
    print(f'Файл с данными по SVD: {Path(svd_directory).absolute()}')
    print(f'Файл с данными по СBOW: {Path(cbow_save_path).absolute()}')

    find_and_process_files(source_directory, processed_directory, PARTS_OF_SPEECH, PART_OF_REPLACE)
    make_corpus(directory=processed_directory, corpus_path=corpus_path)

    dict = svd_dict_from_corpus(corpus_path, svd_dict_path, svd_directory, new=True, min_df=4, rank=100)
    convert_npy_dict_to_xlsx(svd_dict_path)

    dict2 = cbow_dict_from_corpus(corpus_path, cbow_save_path, None, new=True, min_df=4, rank=100)
    convert_npy_dict_to_xlsx(cbow_save_path)


if __name__ == '__main__':
    coptic_processing(home='.')
