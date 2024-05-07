import os
import pickle
from random import sample

import gensim.downloader as api
import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from matplotlib import pyplot as plt
from nltk.tokenize import word_tokenize
from sklearn.metrics.pairwise import cosine_distances, manhattan_distances, euclidean_distances
from tqdm import tqdm


def load_model(use_pretrained=True, custom_corpus=None, vector_size=300, window=7, min_count=3):
    model_path = 'custom_word2vec.model'
    if use_pretrained:
        model = api.load('word2vec-google-news-300')
    else:
        if custom_corpus is None:
            raise ValueError("Custom corpus cannot be None if not using the pretrained model")
        if os.path.exists(model_path):
            print('Модель векторизации найдена')
            with open(model_path, 'rb') as m:
                model = pickle.load(m)
        else:
            print('Модель векторизации не найдена')
            sentences = [word_tokenize(text) for text in tqdm(custom_corpus, desc="Tokenizing corpus")]
            model = Word2Vec(sentences, vector_size=vector_size, window=window, min_count=min_count, workers=4)
            with open(model_path, 'wb') as m:
                pickle.dump(model, m)
        model = model.wv
    return model


def analyze_word_distances(model, text, word):
    words = word_tokenize(text)
    valid_words = list(set(w for w in words if w in model.key_to_index))
    if word in model.key_to_index:
        target_vec = model[word]
        vectors = [model[w] for w in valid_words]
        distances = {
            'word': valid_words,
            'cosine': cosine_distances([target_vec], vectors).flatten(),
            'euclidean': euclidean_distances([target_vec], vectors).flatten(),
            'manhattan': manhattan_distances([target_vec], vectors).flatten()
        }
        return pd.DataFrame(distances).sort_values(by='cosine')
    else:
        return pd.DataFrame({'error': ['Word not found in model']})


def compare_word2vec_models(model_custom, num_samples=10000):
    print('Загрузка предобученных моделей')
    models_pretrained = [
        api.load('word2vec-google-news-300'),
        api.load('glove-wiki-gigaword-300'),
        api.load('fasttext-wiki-news-subwords-300')
    ]
    results = []
    for pretrained_model in tqdm(models_pretrained, desc='Модель'):
        cosine_distances_custom = []
        cosine_distances_pretrained = []

        words = list(set(model_custom.key_to_index.keys()) & set(pretrained_model.key_to_index.keys()))
        for _ in range(num_samples):
            word1, word2 = sample(words, 2)
            cosine_distance_custom = model_custom.similarity(word1, word2)
            cosine_distance_pretrained = pretrained_model.similarity(word1, word2)
            cosine_distances_custom.append(cosine_distance_custom)
            cosine_distances_pretrained.append(cosine_distance_pretrained)

        cosine_distances_custom = np.array(cosine_distances_custom)
        cosine_distances_pretrained = np.array(cosine_distances_pretrained)
        distance = np.abs(cosine_distances_custom - cosine_distances_pretrained)
        results.append((distance * 50).mean())

    labels = ['word2vec-google-news-300', 'glove-wiki-gigaword-300', 'fasttext-wiki-news-subwords-300']
    plt.figure(figsize=(12, 8))
    plt.bar(labels, results)
    print(f'Итоговые результаты составили: {results} для {labels}')
    plt.xlabel('Предобученные модели')
    plt.ylabel('Процентное отличие')
    plt.title('Сравнение с пользовательской моделью')
    plt.ylim(0, 100)

    path = 'comparison_vectorisation.png'
    plt.savefig(path)
    print(f'Результат сохранен в {path}')
    plt.show()


_model = load_model()
