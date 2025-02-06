import typer
import json
import pathlib
import logging

from utils.loc_bills_api import (
    LoCBillsAPI,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

SUBFIELDS = {"subjects": "subjects", "summaries": "summaries", "textVersions": "text"}


def get_page_bills_data(
    api_url: str = "https://api.congress.gov/v3/",
    output_directory: pathlib.Path = pathlib.Path("../local_data/bills/source_data"),
    api_key: str = None,
    source_path: pathlib.Path = None,
):
    if not output_directory:
        pass
    if not api_key:
        pass

    source_data = json.load(source_path.open("r"))

    output_directory.mkdir(parents=True, exist_ok=True)
    bills_api = LoCBillsAPI(api_url, api_key)
    for bill_data in source_data.get("bills"):
        congress = bill_data.get("congress")
        house = bill_data.get("type").lower()
        bill_no = bill_data.get("number")
        bill_path = f"{congress}/{house}/{bill_no}"
        logger.info(f"Fetching {bill_path}")
        full_bill_data = bills_api.get_bill(congress, house, bill_no)
        bill_output_dir = output_directory / bill_path
        bill_output_dir.mkdir(parents=True, exist_ok=True)
        bill_output_path = bill_output_dir / "bill.json"
        json.dump(full_bill_data, bill_output_path.open("w"), indent=2)
        for subfield_name, url_name in SUBFIELDS.items():

            if full_bill_data.get("bill").get(subfield_name):
                logger.info(f"Fetching {bill_path} - {url_name}")
                subfield_data = bills_api.get_bill_subfield(
                    congress, house, bill_no, url_name
                )
                subfield_output_path = bill_output_dir / f"{url_name}.json"
                json.dump(subfield_data, subfield_output_path.open("w"), indent=2)

                if subfield_name == "textVersions":
                    for item in subfield_data.get("textVersions"):
                        for format in item.get("formats"):
                            if format.get("type") == "Formatted XML":
                                url = format.get("url")
                                logger.info(f"Fetching {bill_path} - {url}")
                                file_name = url.split("/")[-1]
                                bill_text = bills_api.get_bill_text(url)
                                bill_text_path = bill_output_dir / file_name
                                bill_text_path.write_text(bill_text)


if __name__ == "__main__":
    typer.run(get_page_bills_data)
