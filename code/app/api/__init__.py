import requests 
from math import floor
from datetime import datetime
from retry import retry

class UispApi:

    @retry(requests.exceptions.HTTPError, tries=10, delay=1, backoff=2)
    def get_request(self, endpoint, params):
        kwargs = {
            'url': f'{self.url}{endpoint}',
            'headers': {
                'accept': 'application/json',
                'x-auth-token': self.api_key,
            },
            'params': params,
        }
        response = requests.get(**kwargs)
        response.raise_for_status()
        return response

    def __init__(self, domain, api_version, api_key):
        self.url = f'https://{domain}/nms/api/{api_version}'
        self.api_key = api_key

    def get_outages(self, site_id: str, from_datetime: datetime):
        start_timestamp = floor(from_datetime.timestamp() * 1_000)
        endpoint = '/outages'
        params = {
            'siteId': [site_id],
            'count': 1_000,
            'page': 1,
            'start': start_timestamp,
        }
        return self.get_request(endpoint, params)

    def get_sites(self, site_ids: list[str] | None = None):
        if site_ids is None:
            site_ids = []
        endpoint = '/sites'
        params = {
            'id': site_ids
        }
        return self.get_request(endpoint, params)

    def get_site_by_name(self, site_name: str) -> str:
        endpoint = '/sites/search'
        params = {
            'query': site_name,
            'count': 1,
            'page': 1,
        }
        return self.get_request(endpoint, params)

def get_site_id_from_search_response(response: requests.Response) -> str:
    response.raise_for_status()
    results = response.json()
    if len(results) == 1:
        return results[0]['id']
    elif len(results) == 0:
        raise Exception('No matching results for site search')
    elif len(results) > 1:
        raise Exception('Too many matching results for site search')
    raise Exception('Unspecified error')
