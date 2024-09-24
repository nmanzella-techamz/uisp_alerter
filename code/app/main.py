import tomllib
from datetime import datetime, timedelta
from rich import print
from api import UispApi, get_site_id_from_search_response
from helpers import create_alert_message
from dateutil import tz
from mail import send_uisp_alert
import requests
import os

config_path = os.environ.get('UISP_ALERTER_CONFIG_PATH')
if not config_path:
    raise Exception('An Environment Variable with a key named "UISP_ALERTER_CONFIG_PATH" and a value that points to the "config.toml" file must exist.')

with open(config_path, 'rb') as f:
    config = tomllib.load(f)

api = UispApi(**config['api'])

ignore_alerts_less_than = config['ignore_alerts']['less_than']

if __name__ == "__main__":
    for notification in config['notifications']:
        search_response = api.get_site_by_name(notification['site_name'])
        site_id = get_site_id_from_search_response(search_response)
        timezone = tz.gettz(notification['timezone'])
        now = datetime.now(timezone) 
        time_span = timedelta(**config['time_span'])
        date_in_past = now - time_span
        outages = api.get_outages(site_id=site_id, from_datetime=date_in_past)
        try:
            outages.raise_for_status()
        except requests.exceptions.HTTPError:
            print(f'HTTP Error during Outages request: {outages.status_code} {outages.reason}')
            continue
        items = outages.json()['items'] 
        print(items)
        alerts = [create_alert_message(outage, timezone) for outage in items \
                  if outage['aggregatedTime'] > ignore_alerts_less_than]
        print(f'Number of alerts: {len(alerts)}')
        if len(alerts) > 0:
            send_uisp_alert(alerts=alerts,
                            site_name=notification['site_name'],
                            to_emails=notification['emails'],
                            from_email=config['mail']['from'],
                            password=config['mail']['password'],
                            timezone=notification['timezone'],
                            time_span=time_span)