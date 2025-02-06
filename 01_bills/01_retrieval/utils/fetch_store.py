import json
import logging

from pathlib import Path

from .api import (
    LoCBillsAPI,
)

BILL_SUBFIELDS = {
    "subjects": "subjects",
    "summaries": "summaries",
    "textVersions": "text",
}
TEXT_SUBFIELD = "textVersions"

logger = logging.getLogger(__name__)


def _update_source_page_status(
    source_page_path: str,
    source_page_json: dict,
    status_path: Path,
):
    return status_path
    status = json.load(status_path.open())
    if source_page_json:
        for bill_data in source_page_json.get("bill", []):
            congress = int(bill_data.get("congress"))
            house = bill_data.get("type").lower()
            bill_number = int(bill_data.get("number"))
            bill_path = f"{congress}/{house}/{bill_number}"
            status["bills"][bill_path] = {
                "processed": False,
            }
    json.dump(status, status_path.open("w"), indent=2)
    return status_path


def _initialise_source_page_status(
    source_page_path: str,
    source_page_json: dict,
    status_path: Path,
):
    status = {"source": source_page_path, "bills": {}}
    if source_page_json:
        for bill_data in source_page_json.get("bills", []):
            congress = int(bill_data.get("congress"))
            house = bill_data.get("type").lower()
            bill_number = int(bill_data.get("number"))
            bill_path = f"{congress}/{house}/{bill_number}"
            status["bills"][bill_path] = {
                "processed": False,
            }
    json.dump(status, status_path.open("w"), indent=2)
    return status_path


def fetch_and_store_bills_source_page(
    bills_api: LoCBillsAPI,
    congress: int,
    output_directory: Path,
    page_offset: int,
    page_limit: int,
    overwrite: bool,
):
    """
    Get a single page from the congress.gov API
    from the /bill/bill_list_by_congress endpoint,
    save this page in the location provided and
    return the pagination information from the page data.
    """
    logger.info(f"Processing page: ({congress=}, {page_offset=})")
    dest_path = output_directory / f"{congress}_{page_offset}.json"
    status_path = output_directory / f"{congress}_{page_offset}.status.json"
    source_page_json = {}
    if dest_path.exists() and not overwrite:
        logger.debug(f"Page JSON already present: ({dest_path=})")
    else:
        source_page_json = bills_api.get_congress_bills_page(
            congress=congress, page_offset=page_offset, page_limit=page_limit
        )
        json.dump(source_page_json, dest_path.open("w"), indent=2)
        logger.debug(f"Stored page JSON: ({dest_path=})")
    if status_path.exists() and not overwrite:
        logger.debug(f"Page status JSON already present: ({status_path=})")
        _ = _update_source_page_status(
            source_page_path=str(dest_path),
            source_page_json=source_page_json,
            status_path=status_path,
        )
    else:
        _ = _initialise_source_page_status(
            source_page_path=str(dest_path),
            source_page_json=source_page_json,
            status_path=status_path,
        )
    return dest_path


def fetch_and_store_congress_bills_source_pages(
    api_url: str,
    api_key: str,
    congress: int,
    output_directory: Path,
    page_limit: int,
    overwrite: bool,
):
    """
    Get all pages of bills for the provided congress from the congress.gov API
    from the /bill/bill_list_by_congress endpoint,
    and save them in the output directory provided.
    """
    output_directory.mkdir(parents=True, exist_ok=True)
    bills_api = LoCBillsAPI(api_url, api_key)
    page_offset = 0
    dest_path = fetch_and_store_bills_source_page(
        bills_api=bills_api,
        congress=congress,
        output_directory=output_directory,
        page_offset=page_offset,
        page_limit=page_limit,
        overwrite=overwrite,
    )
    pagination_data = json.load(dest_path.open("r")).get("pagination")
    total_items = pagination_data.get("count")
    pages = list(range(page_limit, total_items + 1, page_limit))
    logger.info(f"Remaining pages: ({len(pages)=}, {total_items=})")
    for offset in pages:
        _ = fetch_and_store_bills_source_page(
            bills_api=bills_api,
            congress=congress,
            output_directory=output_directory,
            page_offset=offset,
            page_limit=page_limit,
            overwrite=overwrite,
        )


def fetch_and_store_subfield_data(
    bills_api: LoCBillsAPI,
    congress: int,
    house: str,
    bill_number: int,
    subfield_name: str,
    bill_json: dict,
    output_directory: Path,
    overwrite: bool,
):
    if bill_json.get("bill").get(subfield_name):

        url_name = BILL_SUBFIELDS.get(subfield_name)
        logger.debug(f"Subfield present: {subfield_name}")
        subfield_output_path = output_directory / f"{url_name}.json"
        if subfield_output_path.exists() and not overwrite:
            if subfield_name == TEXT_SUBFIELD:
                logger.debug(f"Loading existing subfield: {subfield_output_path}")
                subfield_json = json.load(subfield_output_path.open("r"))
            else:
                logger.debug(f"Skipping existing subfield: {subfield_output_path}")
                return
        else:
            subfield_json = bills_api.get_bill_subfield(
                congress, house, bill_number, url_name
            )
            json.dump(subfield_json, subfield_output_path.open("w"), indent=2)
            logger.debug(f"Stored bill subfield JSON: {subfield_output_path}")
        if subfield_name == TEXT_SUBFIELD:
            for text_version in subfield_json.get("textVersions"):
                for format in text_version.get("formats"):
                    if format.get("type") == "Formatted XML":
                        url = format.get("url")
                        text_file_name = url.split("/")[-1]
                        bill_text_path = output_directory / text_file_name
                        if bill_text_path.exists() and not overwrite:
                            logger.debug(
                                f"Skipping existing bill text: {bill_text_path}"
                            )
                        else:
                            bill_text = bills_api.get_bill_text(url)
                            bill_text_path.write_text(bill_text)
                            logger.debug(f"Stored bill text: {bill_text_path}")
        return


def fetch_and_store_bill_data(
    bills_api: LoCBillsAPI,
    congress: int,
    house: str,
    bill_number: int,
    output_directory: Path,
    overwrite: bool,
):
    """
    Fetch the detailed data for a bill from the congress.gov API
    from the /bill/bill_details endpoint (/bill/{congress}/{house}/{bill_number}),
    save this at the subpath /{congress}/{house}/{bill_number}/bill.json of the provided output location.
    For each of the subfields specified in the BILL_SUBFIELDS that are present in the detailed bill data,
    fetch the subfield data from the congress.gov API and store alongside the bill.json (e.g. text.json).
    When the subfield is `textVersions`, also fetch all iterations of the bill text in the XML format and store alongside bill.json.
    """
    logger.info(f"Processing Bill: ({congress=}, {house=}, {bill_number=})")
    bill_path = f"{congress}/{house}/{bill_number}"
    bill_output_dir = output_directory / bill_path
    bill_output_dir.mkdir(parents=True, exist_ok=True)
    bill_output_path = bill_output_dir / "bill.json"
    if bill_output_path.exists() and not overwrite:
        logger.debug(f"Loading existing: {bill_output_path}")
        bill_json = json.load(bill_output_path.open("r"))
    else:
        bill_json = bills_api.get_bill(congress, house, bill_number)
        json.dump(bill_json, bill_output_path.open("w"), indent=2)
        logger.debug(f"Stored base bill JSON: {bill_output_path}")
    for subfield_name in BILL_SUBFIELDS.keys():
        subfield_data = fetch_and_store_subfield_data(
            bills_api=bills_api,
            congress=congress,
            house=house,
            bill_number=bill_number,
            subfield_name=subfield_name,
            bill_json=bill_json,
            output_directory=bill_output_dir,
            overwrite=overwrite,
        )


def fetch_and_store_bills_from_source_page(
    api_url: str,
    api_key: str,
    source_path: Path,
    output_directory: Path,
    overwrite: bool,
):
    source_data = json.load(source_path.open("r"))

    output_directory.mkdir(parents=True, exist_ok=True)
    bills_api = LoCBillsAPI(api_url, api_key)
    page_bills = source_data.get("bills")
    total_bills = len(page_bills)
    for count, bill_data in enumerate(source_data.get("bills"), start=1):
        logger.info(f"{count}/{total_bills}")
        congress = int(bill_data.get("congress"))
        house = bill_data.get("type").lower()
        bill_number = int(bill_data.get("number"))
        bill_info = fetch_and_store_bill_data(
            bills_api=bills_api,
            congress=congress,
            house=house,
            bill_number=bill_number,
            output_directory=output_directory,
            overwrite=overwrite,
        )
