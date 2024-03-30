import glob
import os
import fnmatch
from tqdm import tqdm
from conllu import parse


def process_file(input_path, output_directory, parts_of_speech, parts_of_replace=None):
    """Функция для обработки одного файла"""
    # Чтение содержимого файла
    with open(input_path, 'r', encoding='utf-8') as file:
        data = file.read()

    if data == '':
        return

    parsed_data = parse(data)

    processed_text = []
    for sentence in parsed_data:
        for token in sentence:
            if token['upos'] in parts_of_speech:
                # Добавляем нормальную форму, если она доступна и не равна прочерку или None
                lemma = token['lemma']
                if lemma and lemma not in ['-', 'None', '_warn:empty_norm_', 'ⲻⲻ']:
                    processed_text.append(lemma)
            elif token['upos'] in parts_of_replace:
                # Заменяем слово на указанное значение в словаре parts_of_replace
                replacement = parts_of_replace[token['upos']]
                processed_text.append(replacement)

    base_name = os.path.basename(input_path)
    output_path = os.path.join(output_directory, base_name.replace('.conllu', '.txt'))

    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(' '.join(processed_text))


def find_files(directory, extension):
    """Генератор, возвращающий пути файлов с заданным расширением."""
    for root, dirs, files in os.walk(directory):
        for file in fnmatch.filter(files, f"*.{extension}"):
            yield os.path.join(root, file)


def find_and_process_files(source_directory, output_directory, parts_of_speech, parts_of_replace=None):
    # Собираем все пути файлов в список для отображения прогресса
    files_to_process = list(find_files(source_directory, "conllu"))

    # Используем tqdm для отображения прогресса
    for file_path in tqdm(files_to_process, desc="Обработка файлов"):
        process_file(file_path, output_directory, parts_of_speech, parts_of_replace)


def make_corpus(directory, corpus_path):
    file_list = sorted(glob.glob(directory + '/*'))
    with open(corpus_path, 'w', encoding='utf-8') as output_file:
        for file in tqdm(file_list, desc="Создание корпуса"):
            with open(file, 'r', encoding='utf-8') as input_file:
                output_file.write(input_file.read().replace('\n', ' '))
                output_file.write('\n')


if __name__ == "__main__":
    source_directory = input("Введите путь к входной директории: ")
    output_directory = input("Введите путь к выходной директории: ")
    parts_of_speech = ['NOUN', 'VERB']
    parts_of_replace = {
        'PROPN': 'person1',
        'PRON': 'pron1',
        'NUM': 'ordinal1'
    }
    find_and_process_files(source_directory, output_directory, parts_of_speech)
