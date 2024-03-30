from pathlib import Path

from scipy.sparse.linalg import svds
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer


def make_matrix_W_list_of_words(corpus_path, min_df, max_df=None, token_pattern=None, use_idf=True):
    '''
    corpus_path - is a path to the corpus, where one line - one text

    min_df - is the minimum times (or fraction of the texts) a word must occur in the corpus

    max_df - is the maximum times (or fraction of the texts) a word must occur in the corpus
    if it is None, there are no upper bound

    token_pattern - alphabet, which will be considered. Usually can be all letters of the language and numbers
    if None all symbols will be OK

    use_idf - is bool value whether to use idf
    '''
    with open(corpus_path, 'r', encoding='utf-8') as corpus_file:
        if token_pattern:
            vectorizer = TfidfVectorizer(analyzer='word', min_df=min_df, token_pattern=token_pattern, use_idf=use_idf)
        else:
            vectorizer = TfidfVectorizer(analyzer='word', min_df=min_df, use_idf=use_idf)
        data_vectorized = vectorizer.fit_transform(corpus_file)
    return data_vectorized, vectorizer.get_feature_names_out()


def apply_svd(W, k, output_folder):
    '''
    W - matrix texts x words
    k - the rank of the SVD, must be less than any dimension of W
    '''
    # Apply the SVD function
    u, sigma, vt = svds(W, k)

    # The function does not garantee, that the order of the singular values is descending
    # So, we need to dreate it by hand
    descending_order_of_inds = np.flip(np.argsort(sigma))
    u = u[:, descending_order_of_inds]
    vt = vt[descending_order_of_inds]
    sigma = sigma[descending_order_of_inds]

    # Checking that sizes are ok
    assert sigma.shape == (k,)
    assert vt.shape == (k, W.shape[1])
    assert u.shape == (W.shape[0], k)

    # Now, we'll save all the matrixes in folder (just in case)
    with open(output_folder + '/' + str(k) + '_sigma_vt.npy', 'wb') as f:
        np.save(f, np.dot(np.diag(sigma), vt).T)
    with open(output_folder + '/' + str(k) + '_sigma.npy', 'wb') as f:
        np.save(f, sigma)
    with open(output_folder + '/' + str(k) + '_u.npy', 'wb') as f:
        np.save(f, u)
    with open(output_folder + '/' + str(k) + '_vt.npy', 'wb') as f:
        np.save(f, vt)
    return np.dot(np.diag(sigma), vt).T


def create_dictionary(words_list, vv, output_file):
    dictionary = {}
    for word, vector in zip(words_list, vv):
        dictionary[word] = vector
    np.save(output_file, dictionary)
    return dictionary


def svd_dict_from_corpus(corpus_path, dict_file, output_folder, rank=5, new=True, min_df=1):
    print(f'[INFO] SVD: Файл словаря находится в {Path(dict_file).absolute()}')
    if new is False:
        return np.load(dict_file, allow_pickle=True)[()]
    W, words_list = make_matrix_W_list_of_words(corpus_path, min_df)
    print(f'[INFO] SVD: Всего слов - {len(words_list)}')
    return create_dictionary(words_list, apply_svd(W, rank, output_folder), dict_file)
