import ast
import os
from typing import Optional

import networkx as nx
from tqdm import tqdm

from graphs_construction.prompt_config import PROMPT


class SemanticRelation:
    def __init__(self, rel_type, subtype, name):
        self.rel_type = rel_type
        self.subtype = subtype
        self.name = name

    def __str__(self):
        return f'Type: {self.rel_type.lower()}, Subtype: {self.subtype.lower()}, Name: {self.name}'


DICT = {
    'HIERARCHICAL': {
        'ISA': ['member_of', 'instance_of'],
        'AKO': ['subset_of'],
        'PARTITIVE': ['has_part']
    },

    'AUXILIARY': {
        'FUNCTIONAL': ['produces', 'affects'],
        'QUANTITATIVE': ['more_than', 'less_than', 'equal_to'],
        'SPATIAL': ['far_from', 'close_to', 'behind', 'under', 'above'],
        'TEMPORAL': ['before', 'after', 'during'],
        'ATTRIBUTIVE': ['has_property', 'has_value']
    },
}

default_style = {'color': 'black', 'width': 1, 'dashes': True}


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
    return SemanticRelation(rel_type=rel_type, subtype=subtype, name=name)


def text_to_windows(text, window_size=20, step=5):
    words = text.split()
    for i in range(0, len(words) - window_size + 1, step):
        yield ' '.join(words[i:i + window_size])


def load_network(text=None, openai_client=None, checkpoint_step=100):
    path = 'network.graphml'
    checkpoint_path = 'network_backup_{}.graphml'
    if os.path.exists(path):
        try:
            return nx.read_graphml(path)
        except Exception as e:
            print(f'error with loading {path}: {e}')
            return None

    if openai_client is None or text is None:
        return None

    network = nx.DiGraph()
    for index, window in tqdm(enumerate(text_to_windows(text))):
        if index % checkpoint_step == 0:
            nx.write_graphml(network, checkpoint_path.format(index))
        dependencies = dependency_extractor(window, openai_client)
        for src, relation, dst in dependencies:
            network.add_edge(src, dst, label=relation.__str__())
    nx.write_graphml(network, path)
    return network


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
        print(f'Unexpected error: {e}')
        pass
    return answer
