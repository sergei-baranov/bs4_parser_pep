import argparse
import csv
import datetime as dt
import logging
from pathlib import Path

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT


def control_output(results: list, cli_args: argparse.ArgumentParser):
    output = cli_args.output

    if output == 'pretty':
        pretty_output(results)
    elif output == 'file':
        file_output(results, cli_args)
    else:
        default_output(results)


def default_output(results: list):
    for row in results:
        print(*row)


def pretty_output(results: list):
    table = PrettyTable()
    # В качестве заголовков устанавливаем первый элемент списка.
    table.field_names = results[0]
    # Выравниваем всю таблицу по левому краю.
    table.align = 'l'
    # Добавляем все строки, начиная со второй (с индексом 1).
    table.add_rows(results[1:])
    # Печатаем таблицу.
    print(table)


def file_output(results: list, cli_args: argparse.ArgumentParser):
    # всё норм, для типа данных переопределён оператор '/'
    results_dir: Path = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)

    parser_mode: str = cli_args.mode
    now: dt.datetime = dt.datetime.now()
    now_formatted: str = now.strftime(DATETIME_FORMAT)
    file_name: str = f'{parser_mode}_{now_formatted}.csv'
    file_path: Path = results_dir / file_name

    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect='unix')
        writer.writerows(results)

    logging.info(f'Файл с результатами был сохранён: {file_path}')
