import ast
import os
import pickle
from random import sample
from typing import Optional, Dict, List

import gensim.downloader as api
import matplotlib.pyplot as plt
import nltk
import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize
from openai import OpenAI
from sklearn.metrics.pairwise import euclidean_distances, cosine_distances, manhattan_distances
from tqdm import tqdm

from prompt_configuration import PROMPT

nltk.download('punkt')


def load_model(use_pretrained=True, custom_corpus=None, vector_size=300, window=7, min_count=3):
    """ Загрузка модели Word2Vec в зависимости от выбора: предобученная или обученная на пользовательском корпусе. """
    model_path = 'custom_word2vec.model'
    if use_pretrained:
        model = api.load('word2vec-google-news-300')  # Загрузка предобученной модели
    else:
        if custom_corpus is None:
            raise ValueError("Custom corpus cannot be None if not using the pretrained model")
        if os.path.exists(model_path):
            print('Модель найдена')
            with open(model_path, 'rb') as m:
                model = pickle.load(m)
        else:
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
        return calculate_distances(target_vec, vectors, valid_words)
    else:
        return pd.DataFrame({'error': ['Word not found in model']})


def calculate_distances(target_vec, vectors, words):
    distances = {
        'word': words,
        'cosine': cosine_distances([target_vec], vectors).flatten(),
        'euclidean': euclidean_distances([target_vec], vectors).flatten(),
        'manhattan': manhattan_distances([target_vec], vectors).flatten()
    }
    return pd.DataFrame(distances).sort_values(by='cosine')


def get_text(corpus_path: str, example_corpus: str = './example_corpus.txt') -> str:
    if os.path.exists(corpus_path):
        with open(corpus_path, 'r', encoding='utf-8') as file:
            return file.read()
    if os.path.exists(example_corpus):
        with open(example_corpus, 'r', encoding='utf-8') as file:
            return file.read()
    return 'example text because other ways is not accessible'


def compare_models(custom_model, pretrained_models, num_samples=10000):
    results = []

    # Вычисляем процентное отличие для каждой предобученной модели
    for pretrained_model in tqdm(pretrained_models, desc='Модель'):
        cosine_distances_custom = []
        cosine_distances_pretrained = []

        words = list(set(custom_model.key_to_index.keys()) & set(pretrained_model.key_to_index.keys()))

        for _ in range(num_samples):
            word1, word2 = sample(words, 2)

            cosine_distance_custom = custom_model.similarity(word1, word2)
            cosine_distance_pretrained = pretrained_model.similarity(word1, word2)

            cosine_distances_custom.append(cosine_distance_custom)
            cosine_distances_pretrained.append(cosine_distance_pretrained)

        cosine_distances_custom = np.array(cosine_distances_custom)
        cosine_distances_pretrained = np.array(cosine_distances_pretrained)

        distance = np.abs(cosine_distances_custom - cosine_distances_pretrained)
        results.append((distance * 50).mean())

    return results


class SemanticRelation:
    def __init__(self, rel_type, subtype, name):
        self.rel_type = rel_type
        self.subtype = subtype
        self.name = name

    def __str__(self):
        return f'Type: {self.rel_type.lower()}, Subtype: {self.subtype.lower()}, Name: {self.name}'


DICT: Dict[str, Dict[str, List[str]]] = {
    'HIERARCHICAL': {
        'ISA': ['member_of', 'instance_of'],
        'AKO': ['subset_of'],
        'PARTITIVE': ['has_part']
    },

    'AUXILIARY': {
        'FUNCTIONAL': ['produces', 'affects', ],
        'QUANTITATIVE': ['more_than', 'less_than', 'equal_to', ],
        'SPATIAL': ['far_from', 'close_to', 'behind', 'under', 'above', ],
        'TEMPORAL': ['before', 'after', 'during', ]
    },
    'ATTRIBUTIVE': ['has_property', 'has_value'],
    'LOGICAL': ['and', 'or']
}


def get_relation(s: str) -> Optional[SemanticRelation]:
    types = s.split('.')
    if len(types) != 3:
        return None
    rel_type, subtype, name = types
    if rel_type not in DICT:
        return None
    if subtype not in DICT[rel_type]:
        return None
    if name not in DICT[rel_type][subtype]:
        return None

    return SemanticRelation(
        rel_type=rel_type,
        subtype=subtype,
        name=name
    )


def dependency_extractor(fragment, openai_client):
    response = openai_client.chat.completions.create(
        model="gpt-4-turbo-2024-04-09",
        messages=[
            {"role": "system", "content": "you are a professional device for building a tree of knowledge"},
            {"role": "user", "content": PROMPT.format(fragment)},
        ]
    )
    answer = []
    try:
        struct = ast.literal_eval(response.choices[0].message.content)
        for item in struct:
            if len(item) != 3:
                continue
            ent1, rel, ent2 = item
            relation = get_relation(rel)
            if relation is None:
                continue
            answer.append((ent1, relation, ent2))
    except Exception as e:
        pass
    return answer


def build_graphs(corpus_path='corpus.txt'):
    corpus = get_text(corpus_path)
    model_custom = load_model(use_pretrained=False, custom_corpus=corpus.split('\n'))
    print('Модель векторизована')

    word = 'antibiotic'

    # Код для создания excel таблицы на основе слова
    ans = input(f'Начать посторение таблицы косинусных расстояний на своей модели? [y/N] ')
    if ans.lower() == 'y':
        df_custom = analyze_word_distances(model_custom, corpus, word)
        df_custom.to_excel(f'file_{word}_custom.xlsx', index=False)
        print(f'Результат сохранен в file_{word}_custom.xlsx')

    # Код для создания предобученной excel таблицы
    ans = input(f'Начать посторение таблицы косинусных расстояний на предобученной модели? [y/N] ')
    if ans.lower() == 'y':
        model_pretrained = load_model()
        df_pretrained = analyze_word_distances(model_pretrained, corpus, word)
        df_pretrained.to_excel(f'file_{word}_pretrained.xlsx', index=False)
        print(f'Результат сохранен в file_{word}_pretrained.xlsx')

    ans = input('Провести сравнение с предобученными моделями? [y/N] ')
    if ans.lower() == 'y':
        print('Загрузка предобученных моделей')
        models_pretrained = [
            api.load('word2vec-google-news-300'),
            api.load('glove-wiki-gigaword-300'),
            api.load('fasttext-wiki-news-subwords-300')
        ]
        print('Сравнение моделей')
        # Сравним модели
        percent_differences = compare_models(model_custom, models_pretrained)
        # Построим графики
        labels = ['word2vec-google-news-300', 'glove-wiki-gigaword-300', 'fasttext-wiki-news-subwords-300']
        plt.figure(figsize=(12, 8))
        plt.bar(labels, percent_differences)
        print(f'Итоговые результаты составили: {percent_differences} для {labels}')
        plt.xlabel('Предобученные модели')
        plt.ylabel('Процентное отличие')
        plt.title('Сравнение с пользовательской моделью')
        plt.ylim(0, 100)

        plt.savefig('comparison_vectorisation.png')
        plt.show()

    ans = input('Провести построение семантического графа? [y/N] ')
    if ans.lower() == 'y':
        token = input('Пожалуйста, укажите ваш токен для openai api')
        client = OpenAI(api_key=token)
        lst = dependency_extractor('hello, it is a mario', client)
        print(lst)
