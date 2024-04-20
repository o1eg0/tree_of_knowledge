import enchant
from nltk.tokenize import word_tokenize
from tqdm import tqdm

coef_of_useless = 0.2
d = enchant.Dict("en_US")


def filter_english_words(text):
    texts = text.split('\n')
    answer = []
    for line in tqdm(texts, desc='Фильтр текстов'):
        if line.count(' ') / len(line) > coef_of_useless:
            continue

        tokens = word_tokenize(line)

        filtered_words = []
        for word in tokens:
            if d.check(word) or d.check(word.capitalize()):
                filtered_words.append(word)

        answer.append(' '.join(filtered_words))
    return '\n'.join(answer)
