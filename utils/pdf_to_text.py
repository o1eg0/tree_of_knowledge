import logging
from pdfminer.high_level import extract_text
from yadisk import Client


def convert_pdf_to_txt(y: Client, pdf_path: str, txt_path: str):
    try:
        y.download(pdf_path, './file.pdf')
        text = extract_text('./file.pdf')
        with open('./file.txt', 'w', encoding='utf-8') as file:
            file.write(text)
        y.upload('./file.txt', txt_path)
        logging.info(f'{pdf_path} -> {txt_path}')
    except Exception as e:
        logging.error(f'ошибка конвертирования {pdf_path} -> {txt_path}: {e}')
