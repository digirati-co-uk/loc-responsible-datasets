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


def get_congress_bills_source_list(
    api_url: str = "https://api.congress.gov/v3/",
    output_directory: pathlib.Path = "../local_data/bills/source_list",
    api_key: str = None,
    congress: str = "117",
):
    if not output_directory:
        pass
    if not api_key:
        pass

    output_directory.mkdir(parents=True, exist_ok=True)
    bills_api = LoCBillsAPI(api_url, api_key)
    page_offset = 0
    bill_list_page = bills_api.get_congress_bills_page(
        congress, page_offset=page_offset
    )
    logger.info(f"Getting congress {congress} page {page_offset}")
    bill_list_page_path = output_directory / f"{congress}_{page_offset}.json"
    json.dump(bill_list_page, bill_list_page_path.open("w"), indent=2)
    logger.info(f"Saved congress {congress} page {page_offset}")
    total_items = bill_list_page.get("pagination").get("count")
    for page_offset in range(250, total_items + 1, 250):
        bill_list_page_path = output_directory / f"{congress}_{page_offset}.json"
        logger.info(f"Getting congress {congress} page {page_offset}")
        bill_list_page = bills_api.get_congress_bills_page(
            congress, page_offset=page_offset
        )
        json.dump(bill_list_page, bill_list_page_path.open("w"), indent=2)
        logger.info(f"Saved congress {congress} page {page_offset}")


if __name__ == "__main__":
    typer.run(get_congress_bills_source_list)
