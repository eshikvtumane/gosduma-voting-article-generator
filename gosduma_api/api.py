from enum import Enum

import requests


class Format(Enum):
    JSON = 'json'
    XML = 'xml'


class Sort(Enum):
    """Способ сортировки результатов голосования
    date_asc — по дате (по возрастанию)
    date_desc — по дате по убыванию, при этом в рамках одного дня по времени по возрастанию
    date_desc_true — по дате (по убыванию)
    result_asc — по результату (по возрастанию)
    result_desc — по результату (по убыванию)
    """
    DATE_ASK = "date_asc"
    DATE_DESC = "date_desc"
    DATE_DESC_TRUE = "date_desc_true"
    RESULT_ASK = "result_asc"
    RESULT_DESC = "result_desc"


class Method(Enum):
    VOTE_SEARCH = 'voteSearch'
    VOTE = 'vote'
    DEPUTIES = 'deputies'


class Limit(Enum):
    QUANTITY_5 = '5'
    QUANTITY_10 = '10'
    QUANTITY_20 = '20'
    QUANTITY_50 = '50'
    QUANTITY_100 = '100'


class GosDumaApi(object):
    def __init__(self, token, app_token, response_format=Format.JSON):
        self.token = token
        self.app_token = app_token
        self._url = None
        self.response_format = response_format

    def _get_url(self):
        return 'http://api.duma.gov.ru/api/%(token)s/' % {'token': self.token, }

    def _get_result(self, endpoint, params={}):
        link = self._get_url() + endpoint
        params['app_token'] = self.app_token
        if self.response_format == Format.JSON:
            return requests.get(link, params=params).json()
        else:
            return requests.get(link, params=params).text

    def get_vote_search(self, convocation=None, from_data=None, to_date=None, faction=None, deputy=None, number=None,
                        keywords=None, page=1, limit=Limit.QUANTITY_20, sort=Sort.DATE_DESC):
        params = {
            'convocation': convocation,
            'from_data': from_data,
            'to_date': to_date,
            'faction': faction,
            'deputy': deputy,
            'number': number,
            'keywords': keywords,
            'page': page,
            'limit': limit.value,
            'sort': sort.value,
        }
        endpoint = '%(method)s.%(format)s' % {
            'format': self.response_format.value,
            'method': Method.VOTE_SEARCH.value,
        }
        return self._get_result(endpoint, params)

    def vote(self, vote_id):
        endpoint = '%s/%s.%s' % (Method.VOTE.value, vote_id, self.response_format.value)
        return self._get_result(endpoint)

    def get_deputies(self, begin=None, position=None, current=None):
        params = {
            'begin': begin,
            'position': position,
            'current': current,
        }
        endpoint = '%s.%s' % (Method.DEPUTIES.value, self.response_format.value)
        return self._get_result(endpoint, params)
