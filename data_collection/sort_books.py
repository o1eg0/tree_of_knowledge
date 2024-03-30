from yadisk import Client

from utils.find_yadisk_files import define_files


def sort_books(
        y: Client,
        home='KnowledgeDataHub',
        misc_files='{}/MiscFiles',
        raw_files='{}/RawFiles',
        not_found='{}/NotFound',
):
    misc_files = misc_files.format(home)
    raw_files = raw_files.format(home)
    not_found = not_found.format(home)

    print('Сортировка/катологизация происходит на Яндекс.Диске')
    print(f'В вашем корневом каталоге должна быть папка {home}')
    print(f'Папка {misc_files} для ваших неопределенных файлов, они сортируются в соответсвии с именем, которое выступает в роли MD5 хеша')
    print(f'Папка {raw_files} в которую складываются найденые файлы, пример {misc_files}/00de4d53bfab8484eb7da400185c5003 перейдет {raw_files}/english/pdf/Database driven website.pdf')
    print(f'В Папку {not_found} складываются не найденые файлы')
    _ = input('Убедитесь, что эти папки есть у вас на диске. Продолжить?')

    print('[INFO] Проверем файлы...')
    define_files(y, misc_files, raw_files, not_found)
