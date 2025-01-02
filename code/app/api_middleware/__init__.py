from datetime import datetime, timedelta
import requests
from math import floor

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

def timedelta_to_milliseconds(delta: timedelta) -> int:
    milliseconds = int(delta.total_seconds() * 1000)
    return milliseconds

def get_outages_params(site_id: str, start_datetime: datetime, end_datetime: datetime) -> dict:
    delta = end_datetime - start_datetime
    period = timedelta_to_milliseconds(delta)
    start_timestamp = floor(start_datetime.timestamp() * 1_000)
    outages_params = {
        'site_id_list': [site_id],
        'count': 1_000,
        'page': 1,
        'start': start_timestamp,
        'outage_type': ['outage', 'unreachable'],
        'period': period,
    }
    return outages_params