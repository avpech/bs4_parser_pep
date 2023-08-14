import logging
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from requests_cache import CachedSession
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEPS_DOC_URL
from outputs import control_output
from utils import find_tag, find_tag_by_text, get_response


def whats_new(session: CachedSession) -> Optional[List[Tuple[str, str, str]]]:
    """Сбор информации о нововведениях в Python."""
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return None
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all('li', class_='toctree-l1')
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
    return results


def latest_versions(session: CachedSession
                    ) -> Optional[List[Tuple[str, str, str]]]:
    """Сбор информации о статусах версий Python."""
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return None
    soup = BeautifulSoup(response.text, 'lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        raise Exception('Ничего не нашлось')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session: CachedSession) -> None:
    """Скачивание архива с актуальной документацией."""
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    main_tag = find_tag(soup, 'div', attrs={'role': 'main'})
    table_tag = find_tag(main_tag, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag,
        'a',
        attrs={'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    file_name = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / file_name
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session: CachedSession) -> Optional[List[Tuple[str, str]]]:
    """Сбор информации о статусах PEP."""
    response = get_response(session, PEPS_DOC_URL)
    if response is None:
        return None
    soup = BeautifulSoup(response.text, 'lxml')
    section_tag = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    tbody_tag = find_tag(section_tag, 'tbody')
    tr_tags = tbody_tag.find_all('tr')
    results = [('Статус', 'Количество')]
    count_dict: Dict[str, int] = {}
    mismatched_statuses = []
    for tr_tag in tqdm(tr_tags):
        abbr_tag = find_tag(tr_tag, 'abbr')
        a_tag = find_tag(tr_tag, 'a')
        href = a_tag['href']
        pep_link = urljoin(PEPS_DOC_URL, href)
        response = get_response(session, pep_link)
        if response is None:
            continue
        preview_status = abbr_tag.text[1:]
        soup = BeautifulSoup(response.text, 'lxml')
        dt_tag = find_tag_by_text(soup, 'dt', 'Status')
        dd_tag = dt_tag.find_next_sibling()
        abbr_tag = find_tag(dd_tag, 'abbr')
        status = abbr_tag.text
        if status not in EXPECTED_STATUS[preview_status]:
            message = (
                f'Несовпадающие статусы: {pep_link}. '
                f'Статус в карточке: {status}. '
                f'Ожидаемые статусы: {EXPECTED_STATUS[preview_status]}'
            )
            mismatched_statuses.append(message)
        if status in count_dict:
            count_dict[status] += 1
        else:
            count_dict[status] = 1
    for message in mismatched_statuses:
        logging.info(message)
    results.extend(
        sorted(zip(count_dict.keys(), map(str, count_dict.values())))
    )
    results.append(('Total', str(sum(count_dict.values()))))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main() -> None:
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
