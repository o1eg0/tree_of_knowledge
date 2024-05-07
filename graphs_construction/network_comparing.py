import random

import numpy as np
from SPARQLWrapper import SPARQLWrapper, JSON
from tqdm import tqdm

from graphs_construction.word2vec_handling import load_model

__model = load_model()


def random_edge_details(digraph):
    if digraph.edges():
        edge = random.choice(list(digraph.edges(data=True)))
        from_node = edge[0]
        to_node = edge[1]
        attributes = edge[2]

        label = attributes.get('label', None)
        return from_node, to_node, label
    else:
        return None, None, None


def find_dbpedia_relationships(entity1, entity2):
    entity1 = entity1.capitalize()
    entity2 = entity2.capitalize()

    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    query = f"""
    SELECT ?property ?hasValue ?isValueOf
    WHERE {{
      {{
        <http://dbpedia.org/resource/{entity1}> ?property ?hasValue .
        FILTER(str(?hasValue) = "http://dbpedia.org/resource/{entity2}")
      }}
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    relationships = []
    for result in results["results"]["bindings"]:
        prop = result['property']['value'].split('/')[-1]
        if 'wikiPageWiki' in prop:
            prop = 'link'
        if 'hasValue' in result:
            relationships.append((entity1, prop, entity2))
        else:
            relationships.append((entity2, prop, entity1))
        return relationships


def calculate_network_similarities(relation, dbpedia_relations):
    relation_parsed = relation.split('Name: ')[1]
    relation_parsed = relation_parsed.replace('_', ' ')
    relation_parsed = relation_parsed.split()
    similarities = []
    for _, db_relation, _ in dbpedia_relations:
        db_relation_words = db_relation.split()
        similarity = 1 - __model.n_similarity(relation_parsed, db_relation_words)
        similarities.append(similarity)
    return np.mean(similarities) if similarities else 0


def compare_semantic_network(network, num_samples=1000):
    percent_similarities = []
    progress_bar = tqdm(desc='Оценка различия', total=num_samples)
    while True:
        entity1, entity2, relation = random_edge_details(network)
        dbpedia_relations = find_dbpedia_relationships(entity1, entity2)
        if dbpedia_relations is None or len(dbpedia_relations) == 0:
            continue
        similarity = calculate_network_similarities(relation, dbpedia_relations)
        percent_similarities.append(100 - similarity * 50)
        progress_bar.update(1)
        if len(percent_similarities) == num_samples:
            break

    average_similarity = round(np.mean(percent_similarities), 2)
    print(f"Среднее процентное сходство: {average_similarity}%")
