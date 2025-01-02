import tomllib
from datetime import timedelta
from rich import print
from api import UispApi
from api_middleware import get_site_id_from_search_response, get_outages_params
from helpers import (
    create_alert_message,
    convert_milliseconds_to_seconds,
    get_datetime,
    get_datetime_now_with_minute_precision,
    get_timezone,
    create_mail_subject,
    create_mail_body,
)
from mail import send_email
import requests
import os
from dotenv import load_dotenv

load_dotenv()

if not (config_path := os.environ.get("UISP_ALERTER_CONFIG_PATH")):
    raise Exception(
        'An Environment Variable with a key named "UISP_ALERTER_CONFIG_PATH" and a value that points to the "config.toml" file must exist.'
    )

if not (site_config_id := os.environ.get("SITE_CONFIG_ID")):
    raise Exception(
        'An Environment Variable with a key named "SITE_CONFIG_ID" must be set when running this script.'
    )

with open(config_path, "rb") as f:
    config_full = tomllib.load(f)

api = UispApi(**config_full["api"])


def main():
    for config in config_full["site_configs"]:
        if config["id"] != site_config_id:
            continue
        search_response = api.get_site_by_name(config["site_name"])
        site_id = get_site_id_from_search_response(search_response)
        timezone = get_timezone(config["timezone"])
        now = get_datetime_now_with_minute_precision(timezone)
        start_delta = timedelta(**config["start_delta"])
        end_delta = timedelta(**config["end_delta"])
        if end_delta >= start_delta:
            return ValueError("start_delta must be greater than end_delta")
        start_datetime = now - start_delta
        end_datetime = now - end_delta
        outages_params = get_outages_params(site_id, start_datetime, end_datetime)
        outages_response = api.get_outages(**outages_params)
        try:
            outages_response.raise_for_status()
        except requests.exceptions.HTTPError:
            print(
                f"HTTP Error during Outages request: {outages_response.status_code} {outages_response.reason}"
            )
            continue
        outages = outages_response.json()["items"]
        # if len(outages) > 0:
        #     print(outages)
        # else:
        #     print("No items returned from /outages API call.")
        alerts = []
        if config["type"] == "event":
            for outage in outages:
                if (
                    convert_milliseconds_to_seconds(outage["aggregatedTime"])
                    < config["ignore_alerts_less_than"]
                ):
                    continue
                outage_timestamps = [outage["startTimestamp"], outage["endTimestamp"]]
                for outage_timestamp in outage_timestamps:
                    if outage_timestamp is None:
                        continue
                    outage_datetime = get_datetime(outage_timestamp, timezone)
                    print(f"{outage_datetime=}")
                    if start_datetime <= outage_datetime <= end_datetime:
                        alerts.append(create_alert_message(outage, timezone))
                        break
        elif config["type"] == "digest":
            for outage in outages:
                if (
                    convert_milliseconds_to_seconds(outage["aggregatedTime"])
                    < config["ignore_alerts_less_than"]
                ):
                    continue
                alerts.append(create_alert_message(outage, timezone))
        else:
            raise ValueError('A config "type" must be defined ("digest" or "event").')
        print(f"Number of alerts: {len(alerts)}")
        if not config["send_mail"]:
            for alert in alerts:
                print(alert)
            return
        if len(alerts) > 0 or config["send_mail_without_events_found"]:
            print("Sending alert")
            subject = create_mail_subject(
                site_name=config["site_name"], alert_number=len(alerts)
            )

            body = create_mail_body(
                site_name=config["site_name"],
                timezone_name=config["timezone"],
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                alerts=alerts,
            )
            send_email(
                smtp_server=config_full["mail"]["smtp_server"],
                smtp_port=config_full["mail"]["smtp_port"],
                to_emails=config["emails"],
                from_email=config_full["mail"]["from"],
                password=config_full["mail"]["password"],
                subject=subject,
                body=body,
            )
        else:
            print("No alert sent")


if __name__ == "__main__":
    main()
