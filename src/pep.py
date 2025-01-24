import logging
from urllib.parse import urljoin

from bs4 import element
import requests_cache

from constants import MAIN_PEP_URL, EXPECTED_STATUS
from utils import load_page_soup, find_tag


def pep_get_list(
        requests_cache_session: requests_cache.CachedSession) -> list[dict]:
    peps_list_by_mainpage = []

    main_pep_url = MAIN_PEP_URL
    page_soup = load_page_soup(main_pep_url, requests_cache_session)
    if page_soup is None:
        logging.error(f'Не удалось получить ресурс со списком PEP: '
                      f'ошибка запроса к {main_pep_url}')
        return peps_list_by_mainpage

    pep_divisions_tables: element.ResultSet = page_soup.find_all(
        'table', attrs={'class': 'pep-zero-table'})
    tables_counter: int = 0
    table: element.Tag
    for table in pep_divisions_tables:
        tables_counter += 1
        rows_counter: int = 0
        pep_table_rows = table.find_all('tr')
        pep_table_row: element.Tag
        for pep_table_row in pep_table_rows:
            rows_counter += 1
            if rows_counter == 1:  # header
                continue

            cells = pep_table_row.find_all('td')
            if len(cells) < 2:
                logging.info(f'row {rows_counter} of table {tables_counter}'
                             f' has less than 2 columns; skipping')
                continue

            type_n_status_code: str = cells[0].text
            status_code: str = type_n_status_code[1:2]

            pep_number: int = 0
            pep_number_text: str = cells[1].text
            if pep_number_text.isdigit():
                pep_number = int(pep_number_text)
            if not pep_number:
                logging.info(f'row {rows_counter} of table {tables_counter}:'
                             f' can not detect pep number; skipping')
                continue

            pep_anchor: element.Tag = find_tag(cells[1], 'a')
            if pep_anchor is None:
                logging.info(f'row {rows_counter} of table {tables_counter}:'
                             f' can not find anchor element; skipping')
                continue
            pep_url: str = pep_anchor.get('href')
            if pep_url is None:
                logging.info(f'row {rows_counter} of table {tables_counter}:'
                             f' can not get href attribute; skipping')
                continue

            peps_list_by_mainpage.append({
                'number': pep_number,
                'url': pep_url,
                'status_code': status_code,
            })

    return peps_list_by_mainpage


def pep_count_real_statuses(
        requests_cache_session: requests_cache.CachedSession,
        peps_list_by_mainpage: list[dict]
) -> dict[str, int]:
    statuses_counters = {}
    for next_pep_record in peps_list_by_mainpage:
        next_pep_num: int = next_pep_record['number']
        next_pep_url: str = urljoin(MAIN_PEP_URL, next_pep_record['url'])
        pep_page_soup = load_page_soup(next_pep_url, requests_cache_session)
        if pep_page_soup is None:
            logging.error(f'Не удалось загрузить страницу PEP {next_pep_num}:'
                          f' ошибка запроса к {next_pep_url}; skipping')
            continue

        status_dt = pep_page_soup.find(
            lambda tag: tag.name == "dt" and 'Status:' in tag.text)
        if status_dt is None:
            logging.error(f'Не удалось найти элемент dt '
                          f'для статуса PEP {next_pep_num}; skipping')
            continue
        status_dd = status_dt.findNext('dd')
        if status_dd is None:
            logging.error(f'Не удалось найти элемент dd '
                          f'для статуса PEP {next_pep_num}; skipping')
            continue
        full_status = status_dd.text
        statuses_counters[full_status] = (statuses_counters
                                          .get(full_status, 0) + 1)

        status_code = next_pep_record['status_code']
        if status_code in EXPECTED_STATUS:
            avail_statuses = EXPECTED_STATUS[status_code]
            if full_status not in avail_statuses:
                avail_statuses_str = ', '.join(avail_statuses)
                log_string = (f'Несовпадающий статус: {next_pep_url}:\n'
                              f'Статус в карточке: {full_status};\n'
                              f'Ожидаемые статусы: [{avail_statuses_str}].\n')
                logging.info(log_string)

    statuses_counters['Total'] = sum(statuses_counters.values())

    return statuses_counters
