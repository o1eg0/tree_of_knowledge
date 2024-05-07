import nltk
from openai import OpenAI

from graphs_construction.network_comparing import compare_semantic_network
from graphs_construction.semantic_network import load_network
from graphs_construction.visualization import visualize_with_pyvis, find_connected_component
from graphs_construction.word2vec_handling import load_model, analyze_word_distances, compare_word2vec_models
from utils.corpus_extractor import get_text

nltk.download('punkt')
word = 'leader'


def build_graphs(corpus_path='corpus.txt'):
    corpus = get_text(corpus_path)
    model_custom = load_model(use_pretrained=False, custom_corpus=corpus.split('\n'))
    model_pretrained = load_model(use_pretrained=True)
    print('Модель векторизации получена')

    # Код для создания excel таблицы на основе слова
    ans = input(f'Начать посторение таблицы косинусных расстояний на своей модели до слова {word}? [y/N] ')
    if ans.lower() == 'y':
        df_custom = analyze_word_distances(model_custom, corpus, word)
        df_custom.to_excel(f'file_{word}_custom.xlsx', index=False)
        print(f'Результат сохранен в file_{word}_custom.xlsx')

    # Код для создания предобученной excel таблицы
    ans = input(f'Начать посторение таблицы косинусных расстояний на предобученной модели до слова {word}? [y/N] ')
    if ans.lower() == 'y':
        df_pretrained = analyze_word_distances(model_pretrained, corpus, word)
        df_pretrained.to_excel(f'file_{word}_pretrained.xlsx', index=False)
        print(f'Результат сохранен в file_{word}_pretrained.xlsx')

    ans = input('Провести сравнение полученной модели с предобученными? [y/N] ')
    if ans.lower() == 'y':
        compare_word2vec_models(model_custom)

    ans = input('Перейти к семантической сети? [y/N] ')
    if ans.lower() != 'y':
        return

    network = load_network()
    if network is None:
        print('Сеть не найдена, начинается построение')
        token = input('Укажите ваш токен для доступа к api openai, учтите что вам может понадобиться VPN, а также при '
                      'построении сети будет произведено большое количество запросов')
        client = OpenAI(api_key=token)
        network = load_network(text=corpus, openai_client=client)

    print('Сеть получена')
    ans = input(f'Визуализировать компоненту слова {word}? [y/N] ')
    if ans.lower() == 'y':
        sub_network = find_connected_component(network, word)
        visualize_with_pyvis(sub_network, corpus, model_pretrained, word)

    ans = input(f'Провести сравнение семантической сети с DBpedia? [y/N] ')
    if ans.lower() == 'y':
        compare_semantic_network(network)
