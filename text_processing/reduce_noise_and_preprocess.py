import os
from tqdm import tqdm

from yadisk import Client

from text_processing.noise_cleaner.noise_cleaner import NoiseCleaner
from utils import find_files

simple_file = './file.txt'
processed_file = './file.processed'


def reduce_noise_and_preprocess(
        y: Client,
        home='KnowledgeDataHub',
        english_text='{}/TxtFiles/english',
        english_processed='{}/ProcessedFiles/english',
):
    english_text = english_text.format(home)
    english_processed = english_processed.format(home)

    print('[INFO] Очищение текстов началось...')
    files = []
    find_files(y, english_text, files)

    processed_files = []
    find_files(y, english_processed, processed_files)

    processed_names = [path.split('/')[-1] for path in processed_files]
    res = set(_ for _ in files).difference(set(f'disk:/{english_text}/{name}' for name in processed_names))

    for path in tqdm(list(res), desc='Обработка файлов'):
        y.download(path, simple_file)
        name = path.split('/')[-1]

        final_name = name
        final_path = f'{english_processed}/{final_name}'

        if y.exists(final_path):
            continue

        try:
            with open(simple_file, 'r', encoding='utf-8') as file:
                text = file.read()
        except Exception as e:
            continue

        with open(processed_file, 'w', encoding='utf-8') as file:
            file.write(NoiseCleaner(text).process())
        y.upload(processed_file, final_path)

    os.remove(simple_file)
    os.remove(processed_file)
