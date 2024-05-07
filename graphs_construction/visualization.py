import networkx as nx
import numpy as np
from pyvis.network import Network

edge_styles = {
    'hierarchical': {
        'isa': {'color': 'blue', 'width': 2, 'dashes': False},
        'ako': {'color': 'green', 'width': 2, 'dashes': False},
        'partitive': {'color': 'red', 'width': 2, 'dashes': False}
    },
    'auxiliary': {
        'functional': {'color': 'purple', 'width': 1, 'dashes': True},
        'quantitative': {'color': 'orange', 'width': 1, 'dashes': True},
        'spatial': {'color': 'yellow', 'width': 1, 'dashes': True},
        'temporal': {'color': 'grey', 'width': 1, 'dashes': True},
        'attributive': {'color': 'pink', 'width': 3, 'dashes': True}
    }
}

default_style = {'color': 'black', 'width': 1, 'dashes': True}


def find_connected_component(graph, word):
    if word not in graph:
        print(f"No such node '{word}' in the graph.")
        return None
    undirected_network = graph.to_undirected()
    components = list(nx.connected_components(undirected_network))
    target_component = None
    for component in components:
        if word in component:
            target_component = component
            break
    return graph.subgraph(target_component)


def visualize_with_pyvis(graph, corpus, model, word):
    words = list(set(corpus.replace('\n', ' ').split()))

    def safe_similarity(x):
        try:
            return 1 - model.n_similarity(x.split(), word.split())
        except Exception as e:
            print(f"Error calculating similarity for '{x}': {str(e)}")
            return 1e10

    sorted_words = sorted(words, key=safe_similarity)

    net = Network(height="4000px", width="100%", directed=True)
    net.set_options("""
            var options = {
              "physics": {
                "barnesHut": {
                  "gravitationalConstant": -3000,
                  "centralGravity": 0.3,
                  "springLength": 100,
                  "springConstant": 0.04,
                  "damping": 0.09,
                  "avoidOverlap": 0.1
                },
                "maxVelocity": 50,
                "minVelocity": 0.1,
                "timestep": 0.5
              }
            }
            """)

    for node in graph.nodes():
        sim = model.n_similarity(node.split(), word.split())
        sim = np.round(1 - sim, 2)
        net.add_node(node.split()[0], label=f'{node.split()[0]}', title=f'Name: {node.split()[0]}\nSimilarity: {sim}')

    for node in sorted_words[:50]:
        if node not in net.nodes:
            sim = model.n_similarity(word.split(), node.split())
            sim = np.round(1 - sim, 2)
            net.add_node(node.split()[0], label=f'{node.split()[0]}\n{sim}',
                         title=f'Name: {node.split()[0]}\nSimilarity: {sim}', color='gray')

    for u, v, attr in graph.edges(data=True):
        label = attr.get('label', '')
        try:
            label_name = label.split(', ')[2].split(': ')[1]
            type_info = label.split(', ')[0].split(': ')[1]
            subtype_info = label.split(', ')[1].split(': ')[1]
            style = edge_styles.get(type_info, {}).get(subtype_info, default_style)
            sim = model.n_similarity(u.split(), v.split())
            sim = np.round(1 - sim, 2)
            net.add_edge(
                u.split()[0], v.split()[0],
                title=f'Name: {label_name}\nSimilarity: {sim}\nType: {type_info}\nSubtype: {subtype_info}',
                label=f'{label_name}\n{sim}',
                color=style['color'],
                width=style['width'], dashes=style['dashes']
            )
        except Exception as e:
            print(f"Не удалось добавить ребро {u}, {v}, {attr}: {e}")
            continue
    path = f'component_{word}.html'
    net.save_graph(path)
    print(f'Результат сохранен в {path}')
