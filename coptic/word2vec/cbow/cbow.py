import io
from pathlib import Path

import numpy as np
from gensim.models import Word2Vec


def load_corpus(fname):
    fin = io.open(fname, 'r', encoding='utf-8', newline='\n', errors='ignore')
    documents = []
    for line in fin:
        documents.append(line.split())
    return documents


def cbow_dict_from_corpus(corpus_path, dict_file, output_folder, rank=5, new=True, min_df=1):
    print(f'[INFO] CBOW: Файл словаря находится в {Path(dict_file).absolute()}')
    if new is False:
        return np.load(dict_file, allow_pickle=True)[()]
    documents = load_corpus(fname=corpus_path)
    model = Word2Vec(sentences=documents, vector_size=rank, min_count=min_df)
    dictionary = {key: model.wv[key] for key in model.wv.key_to_index}
    np.save(dict_file, dictionary)
    print(f'[INFO] CBOW: Всего слов - {len(dictionary)}')
    return dictionary
