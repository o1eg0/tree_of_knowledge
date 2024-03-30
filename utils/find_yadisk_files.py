import logging

from yadisk import Client
from tqdm import tqdm

from utils.search import Search, SearchType

logging.basicConfig(filename='process_log.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO, encoding='utf-8')
ZEROS = 7

def find_files(y, start_path, files):
    """
    Рекурсивно ищет все файлы в заданной директории
    """
    try:
        items = y.listdir(start_path)
    except Exception as e:
        print(f"[ERROR] Ошибка доступа к {start_path}")
        return

    for item in items:
        if item.type == 'dir':
            find_files(y, item.path, files)
        elif item.type == 'file':
            files.append(item.path)


def define_files(y: Client, start_path, found, not_found):
    files = []
    lib = Search(type=SearchType.MD5)
    find_files(y, start_path, files)
    logging.info('')
    for path in tqdm(files, desc='Обработка файлов'):
        md5 = path.split('/')[-1]
        books = lib.search(md5)

        if books is None or len(books) == 0:
            final_path = f'{not_found}/{md5}'
            logging.warning(f'Файл {md5} не найден')
            if not y.exists(final_path):
                try:
                    y.move(path, final_path)
                except Exception as e:
                    logging.error(f'Ошибка перемещения {path} to {final_path}: {e}')
            else:
                try:
                    y.remove(path)
                except Exception as e:
                    logging.error(f'Ошибка удаления {path}: {e}')
            continue

        book = books[0]
        if not y.exists(f'{found}/{book.lang}'):
            y.mkdir(f'{found}/{book.lang}')
        if not y.exists(f'{found}/{book.lang}/{book.extension}'):
            y.mkdir(f'{found}/{book.lang}/{book.extension}')

        name = f'{str(book.libgen_id).zfill(ZEROS)}_{book.title}.{book.extension}'
        final_path = f'{found}/{book.lang}/{book.extension}/{name}'

        if not y.exists(final_path):
            try:
                y.move(path, final_path)
                logging.info(f'{md5} -> {name}')
            except Exception:
                logging.warning(f'{md5} файл не может быть перемещен')
