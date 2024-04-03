import os

from tqdm import tqdm
from yadisk import Client

from utils.find_yadisk_files import find_files
from utils.pdf_to_text import convert_pdf_to_txt


def convert_pdf_eng_books_to_text(
        y: Client,
        home='KnowledgeDataHub',
        english_pdf_files='{}/RawFiles/english/pdf',
        english_text_files='{}/TxtFiles/english'
):
    english_pdf_files = english_pdf_files.format(home)
    english_text_files = english_text_files.format(home)

    files = []
    print('[INFO] Проверяем файлы с расширением pdf...')
    find_files(y, english_pdf_files, files)

    for path in tqdm(files, desc='Конвертация PDF в текст'):
        name = path.split('/')[-1]

        final_name = name.replace('.pdf', '.txt')
        final_path = f'{english_text_files}/{final_name}'

        if not y.exists(final_path):
            convert_pdf_to_txt(y, path, final_path)
    if os.path.exists('./file.txt'):
        os.remove('./file.txt')
    if os.path.exists('./file.pdf'):
        os.remove('./file.pdf')
