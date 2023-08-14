import logging
from typing import Dict, Optional, Union

from bs4 import BeautifulSoup, Tag
from requests import RequestException
from requests_cache import CachedResponse, CachedSession, OriginalResponse

from constants import ENCODING
from exceptions import ParserFindTagException


def get_response(session: CachedSession, url: str
                 ) -> Union[OriginalResponse, CachedResponse, None]:
    """GET-запрос к url."""
    try:
        response = session.get(url)
        response.encoding = ENCODING
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )
        return None


def find_tag(soup: BeautifulSoup,
             tag: str,
             attrs: Optional[Dict[str, str]] = None
             ) -> Tag:
    """Поиск тега."""
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag


def find_tag_by_text(soup: BeautifulSoup, tag: str, text: str
                     ) -> Tag:
    """Поиск тега по содержащемуся в нем тексту."""
    searched_tag = soup.find(lambda tg: tg.name == tag and text in tg.text)
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} с текстом "{text}"'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
