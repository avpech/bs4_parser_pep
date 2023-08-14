import logging
from argparse import ArgumentParser
from enum import Enum
from logging.handlers import RotatingFileHandler
from typing import Iterable, Tuple

from constants import BASE_DIR, DT_FORMAT, ENCODING, LOG_FORMAT


class OutputType(str, Enum):
    """Допустимые значения для аргумента -o, --output."""
    PRETTY = 'pretty'
    FILE = 'file'

    @classmethod
    def tuple(cls) -> Tuple[str, ...]:
        """Получить кортеж допустимых значений для аргумента -o, --output."""
        return tuple(map(lambda key: key.value, cls))


def configure_argument_parser(available_modes: Iterable) -> ArgumentParser:
    """Конфигурация аргументов командной строки."""
    parser = ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=OutputType.tuple(),
        help='Дополнительные способы вывода данных'
    )
    return parser


def configure_logging() -> None:
    """Конфигурация логгирования."""
    log_dir = BASE_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'parser.log'
    rotating_handler = RotatingFileHandler(
        log_file, maxBytes=10 ** 6, backupCount=5, encoding=ENCODING
    )
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
