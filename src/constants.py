from pathlib import Path

BASE_DIR = Path(__file__).parent
MAIN_DOC_URL = 'https://docs.python.org/3/'
PEPS_DOC_URL = 'https://peps.python.org/'
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
ENCODING = 'utf-8'
CSV_DIALECT = 'unix'
BS_PARSER = 'lxml'

# Регулярное выражение, выделяющее в группы номер версии и статус.
# Например, в строке "Python 3.11 (stable)" сформируются следующие группы:
# первой группе <version> соответствует строка "3.11",
# второй группе <status> соответствует строка "stable".
VERSION_STATUS_REGEX = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

# Регулярное выражение, которому соответствует строка,
# оканчивающаяся на "pdf-a4.zip".
PDF_A4_ZIP_REGEX = r'.+pdf-a4\.zip$'
