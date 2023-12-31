import csv
import datetime as dt
import logging
from argparse import Namespace
from typing import List, Tuple

from prettytable import PrettyTable

from configs import OutputType
from constants import BASE_DIR, CSV_DIALECT, DATETIME_FORMAT, ENCODING


def control_output(results: List[Tuple], cli_args: Namespace) -> None:
    """Управление выводом результатов."""
    output = cli_args.output
    if output == OutputType.PRETTY:
        pretty_output(results)
    elif output == OutputType.FILE:
        file_output(results, cli_args)
    else:
        default_output(results)


def default_output(results: List[Tuple]) -> None:
    """Стандартный вывод результатов в терминал."""
    for row in results:
        print(*row)


def pretty_output(results: List[Tuple]) -> None:
    """Вывод результатов в терминал в табличном формате."""
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results: List[Tuple], cli_args: Namespace) -> None:
    """Вывод результатов в файл."""
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding=ENCODING) as f:
        writer = csv.writer(f, dialect=CSV_DIALECT)
        writer.writerows(results)
    logging.info(f'Файл с результатами был сохранён: {file_path}')
