import os


def get_text(corpus_path: str, example_corpus: str = './example_corpus.txt') -> str:
    if os.path.exists(corpus_path):
        with open(corpus_path, 'r', encoding='utf-8') as file:
            return file.read()
    if os.path.exists(example_corpus):
        with open(example_corpus, 'r', encoding='utf-8') as file:
            return file.read()
    return 'example text because other ways is not accessible'
