import nltk
from nltk import bigrams
from sklearn.feature_extraction.text import TfidfVectorizer
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Предположим, `texts` - это ваш список текстов, каждый текст разделен переводом строки
texts = ["Пример текста номер один", "Текст номер два содержит другие слова"]

# Токенизация и создание биграмм
nltk.download('punkt')
tokenized_texts = [nltk.word_tokenize(text.lower()) for text in texts]
bigrams_lists = [list(bigrams(text)) for text in tokenized_texts]

# Плоский список всех биграмм для TF-IDF
flat_bigrams = [" ".join(bigram) for text in bigrams_lists for bigram in text]

# Расчет TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(flat_bigrams)

# Создание графа
G = nx.Graph()

# Добавление узлов
for bigram in vectorizer.get_feature_names_out():
    G.add_node(bigram)

# Вычисление косинусного сходства и добавление рёбер
cos_sim = cosine_similarity(tfidf_matrix)

# Установим порог сходства для создания ребра
similarity_threshold = 0.2

for i in range(cos_sim.shape[0]):
    for j in range(i+1, cos_sim.shape[1]):
        if cos_sim[i, j] > similarity_threshold:
            G.add_edge(vectorizer.get_feature_names_out()[i], vectorizer.get_feature_names_out()[j], weight=cos_sim[i, j])

# Визуализация графа
plt.figure(figsize=(10, 10))
pos = nx.spring_layout(G, seed=42)  # Для воспроизводимости расположения узлов
nx.draw(G, pos, with_labels=True, node_size=2000, node_color="lightblue", font_size=10, font_weight="bold")
plt.title("Граф Биграмм", size=15)
plt.show()
