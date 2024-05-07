PROMPT = """
Using the provided dictionary DICT which classifies various types of semantic relationships, analyze the text to extract entities, concepts, or objects. Identify the relationships between them as specified in DICT. Here are the relationship categories and their subtypes:

DICT = {{
    RelationshipType.HIERARCHICAL: {{
        HierarchicalSubtypes.ISA: [
            'member_of',
            'instance_of'
        ],
        HierarchicalSubtypes.AKO: [
            'subset_of'
        ],
        HierarchicalSubtypes.PARTITIVE: [
            'has_part'
        ]
    }},

    RelationshipType.AUXILIARY: {{
        AuxiliarySubtypes.FUNCTIONAL: [
            'produces',
            'affects',
        ],
        AuxiliarySubtypes.QUANTITATIVE: [
            'more_than',
            'less_than',
            'equal_to',
        ],
        AuxiliarySubtypes.SPATIAL: [
            'far_from',
            'close_to',
            'behind',
            'under',
            'above',
        ],
        AuxiliarySubtypes.TEMPORAL: [
            'before',
            'after',
            'during',
        ],
        AuxiliarySubtypes.ATTRIBUTIVE: [
            'has_property',
            'has_value',
        ],
        AuxiliarySubtypes.LOGICAL: [
            'and',
            'or',
            'and'
        ]
    }}
}}

Please provide outputs in the format: ((entity1, relationship.type.subtype.relationship, entity2)).

Example Text and Expected Outputs:
Text: "Water freezes into ice."
Output: [('water', 'AUXILIARY.FUNCTIONAL.produces', 'ice')]

Sentence: "The sun shines brightly."
Answer: [('sun', 'AUXILIARY.FUNCTIONAL.affects', 'brightly')]

Incomplete sentence fragments should return an empty list [], since full semantic relationships cannot be determined. ENTITIES ARE ALWAYS SINGLE WORDS, and if an output contains any other format or content, it will be considered an error.

Sentence: "A large golden retriever"
Answer: []

Sentence: "John and his cat went to the park together."
Answer: [('John', 'AUXILIARY.FUNCTIONAL.affects', 'cat'), ('John', 'AUXILIARY.SPATIAL.close_to', 'park'), ('cat', 'AUXILIARY.SPATIAL.close_to', 'park')]

Sentence: "Rain heavily affects crops growth."
Answer: [('rain', 'AUXILIARY.FUNCTIONAL.affects', 'crops')]

Sentence: "Historical artifacts belong to an ancient civilization."
Answer: [('artifacts', 'HIERARCHICAL.ISA.member_of', 'civilization')]

Sentence: "The computer has a fast processor and large memory."
Answer: [('computer', 'HIERARCHICAL.PARTITIVE.has_part', 'processor'), ('computer', 'HIERARCHICAL.PARTITIVE.has_part', 'memory')]

Please note that entities are considered as single words directly from the text, and the function corrects orthographic errors while ignoring incorrectly spelled words not amendable by context. Additionally, incomplete sentence fragments or segments that do not clearly imply a relationship within the defined categories result in an empty output list [].

Sentence: {}
Answer:
"""
