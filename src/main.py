import logging
import re
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL
from outputs import control_output
from pep import pep_get_list, pep_count_real_statuses
from utils import load_page_soup, find_tag


def whats_new(
        requests_cache_session: requests_cache.CachedSession
) -> list[(str, str, str)]:
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]

    page_soup = load_page_soup(whats_new_url, requests_cache_session)
    if page_soup is None:
        return results

    main_div = find_tag(
        page_soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(
        main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'})

    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        version_link = urljoin(whats_new_url, version_a_tag['href'])
        section_soup = load_page_soup(version_link, requests_cache_session)
        if section_soup is None:
            continue

        h1 = find_tag(section_soup, 'h1')
        h1_text = h1.text
        dl = find_tag(section_soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1_text, dl_text)
        )

    return results


def latest_versions(
        requests_cache_session: requests_cache.CachedSession
) -> list[(str, str, str)]:
    main_doc_url = MAIN_DOC_URL

    results = [('Ссылка на документацию', 'Версия', 'Статус')]

    page_soup = load_page_soup(main_doc_url, requests_cache_session)
    if page_soup is None:
        return results

    sidebar = find_tag(
        page_soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')

    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is None:
            version, status = a_tag.text, ''
        else:
            version, status = text_match.group('version', 'status')
        results.append((link, version, status))

    return results


def download(requests_cache_session: requests_cache.CachedSession):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')

    page_soup = load_page_soup(downloads_url, requests_cache_session)
    if page_soup is None:
        logging.info(f'Архив НЕ был загружен и сохранён: '
                     f'ошибка запроса к {downloads_url}')
        return

    main_tag = find_tag(page_soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})

    pdf_a4_tag = find_tag(
        table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url: str = urljoin(downloads_url, pdf_a4_link)

    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = requests_cache_session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(requests_cache_session: requests_cache.CachedSession):
    peps_list_by_mainpage: list[dict] = pep_get_list(requests_cache_session)
    statuses_counters = pep_count_real_statuses(
        requests_cache_session, peps_list_by_mainpage)

    filename = 'results.csv'
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    csv_path = results_dir / filename
    with open(csv_path, 'w') as file:
        csv: str = 'Статус,Количество\n'
        for status, count in statuses_counters.items():
            csv += f'{status},{count}\n'
        file.write(csv)

    logging.info(f'Результат был посчитан и сохранён: {csv_path}')


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    # Запускаем функцию с конфигурацией логов.
    configure_logging()
    # Отмечаем в логах момент запуска программы.
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    # Логируем переданные аргументы командной строки.
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode

    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)
    # Логируем завершение работы парсера.
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
