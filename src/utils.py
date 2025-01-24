import logging

from requests import RequestException
from bs4 import BeautifulSoup
import requests_cache

from exceptions import ParserFindTagException


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )


def load_page_soup(
        page_url: str,
        requests_cache_session: requests_cache.CachedSession,
) -> BeautifulSoup:
    response = get_response(requests_cache_session, page_url)

    if response is not None:
        return BeautifulSoup(response.text, features='lxml')


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
