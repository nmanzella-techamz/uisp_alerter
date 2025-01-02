import requests
from retry import retry
from typing import Any


class UispApi:
    @retry(requests.exceptions.HTTPError, tries=5, delay=1, backoff=2)
    def get_request(self, endpoint: str, params: dict[str, Any]) -> requests.Response:
        kwargs = {
            "url": f"{self.url}{endpoint}",
            "headers": {
                "accept": "application/json",
                "x-auth-token": self.api_key,
            },
            "params": params,
        }
        response = requests.get(**kwargs)
        response.raise_for_status()
        return response

    def __init__(self, domain, api_version, api_key) -> None:
        self.url = f"https://{domain}/nms/api/{api_version}"
        self.api_key = api_key

    def get_outages(
        self,
        site_id_list: list[str],
        count: int,
        page: int,
        start: int,
        outage_type: list[str],
        period: int,
    ) -> requests.Response:
        endpoint = "/outages"
        params = {
            "siteId": site_id_list,
            "count": count,
            "page": page,
            "start": start,
            "type": outage_type,
            "period": period,
        }
        return self.get_request(endpoint, params)

    def get_sites(self, site_ids: list[str] | None = None) -> requests.Response:
        if site_ids is None:
            site_ids = []
        endpoint = "/sites"
        params = {"id": site_ids}
        return self.get_request(endpoint, params)

    def get_site_by_name(self, site_name: str, count: int = 1, page: int = 1) -> requests.Response:
        endpoint = "/sites/search"
        params = {
            "query": site_name,
            "count": count,
            "page": page,
        }
        return self.get_request(endpoint, params)
