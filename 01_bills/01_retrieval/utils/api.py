import requests
import logging
import pathlib
import urllib.parse
from requests.adapters import HTTPAdapter, Retry

json_headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": requests.utils.default_user_agent(),
}

logger = logging.getLogger(__name__)

logger = logging.getLogger("ray")
logger.setLevel(logging.DEBUG)

BILL_SUBFIELDS = {
    "subjects": "subjects",
    "summaries": "summaries",
    "textVersions": "text",
}
TEXT_SUBFIELD = "textVersions"
TEXT_TYPES = ["Formatted Text", "Formatted XML"]


class LoCBillsAPI(object):
    def __init__(self, api_url, api_key):

        self.split_api_url = urllib.parse.urlsplit(api_url)
        self.api_key = api_key

        self.session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=1, status_forcelist=[500, 520, 522, 524]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def get_endpoint_json(self, api_path, qs):
        path = pathlib.Path(self.split_api_url.path) / api_path
        url_components = (
            self.split_api_url.scheme,
            self.split_api_url.netloc,
            str(path),
            "",
            "",
        )
        url = urllib.parse.urlunsplit(url_components)
        logger.debug(f"GET: {url=} {qs=}")
        qs["api_key"] = self.api_key
        response = self.session.get(url, params=qs, headers=json_headers)
        response.raise_for_status()
        resp_json = response.json()
        return resp_json

    def get_congress_bills_page(self, congress, page_offset, page_limit):
        path = f"bill/{congress}"
        qs = {"limit": page_limit, "offset": page_offset}
        resp = self.get_endpoint_json(path, qs)
        return resp

    def get_bill(self, congress, house, number):
        path = f"bill/{congress}/{house}/{number}"
        resp = self.get_endpoint_json(path, qs={})
        return resp

    def get_bill_subfield(self, congress, house, number, subfield):
        path = f"bill/{congress}/{house}/{number}/{subfield}"
        resp = self.get_endpoint_json(path, qs={})
        return resp

    def get_bill_text(self, url):
        logger.debug(f"GET: {url=}")
        response = self.session.get(url)
        response.raise_for_status()
        resp_data = response.text
        return resp_data
