import json
import logging
import typing
from pathlib import Path

import fsspec

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

logger = logging.getLogger("ray")
logger.setLevel(logging.DEBUG)


def _initialise_source_page_status(
    source_page_path: str,
    source_page_json: dict,
    status_path: str,
    filesystem: fsspec.filesystem,
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
    json.dump(status, filesystem.open(status_path, "w"), indent=2)
    return status_path


def fetch_and_store_bills_source_page(
    bills_api: LoCBillsAPI,
    congress: int,
    output_location: str,
    filesystem: fsspec.filesystem,
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
    dest_path = f"{output_location}{congress}_{page_offset}.json"
    status_path = f"{output_location}{congress}_{page_offset}.status.json"
    source_page_json = {}
    if filesystem.exists(dest_path) and not overwrite:
        logger.debug(f"Page JSON already present: ({dest_path=})")
    else:
        source_page_json = bills_api.get_congress_bills_page(
            congress=congress, page_offset=page_offset, page_limit=page_limit
        )
        json.dump(source_page_json, filesystem.open(dest_path, "w"), indent=2)
        logger.debug(f"Stored page JSON: ({dest_path=})")
    if filesystem.exists(status_path) and not overwrite:
        logger.debug(f"Page status JSON already present: ({status_path=})")
    else:
        _ = _initialise_source_page_status(
            source_page_path=dest_path,
            source_page_json=source_page_json,
            status_path=status_path,
            filesystem=filesystem,
        )
        logger.debug(f"Stored page status JSON: ({dest_path=})")
    return dest_path


def init_location(
    location: str, is_dir: bool = False, is_dest: bool = False
) -> tuple[fsspec.filesystem, str]:
    if is_dir:
        location = location.rstrip("/") + "/"
    if location.startswith("s3://"):
        fs = fsspec.filesystem("s3")
    else:
        fs = fsspec.filesystem("file")
        if is_dest:
            _path = Path(location)
            if is_dir:
                _path.mkdir(parents=True, exist_ok=True)
            else:
                _path.parent.mkdir(parents=True, exist_ok=True)
    return fs, location


def fetch_and_store_congress_bills_source_pages(
    api_url: str,
    api_key: str,
    congress: int,
    output_location: str,
    page_limit: int,
    overwrite: bool,
):
    """
    Get all pages of bills for the provided congress from the congress.gov API
    from the /bill/bill_list_by_congress endpoint,
    and save them in the output directory provided.
    """

    filesystem, output_location = init_location(
        output_location, is_dir=True, is_dest=True
    )
    bills_api = LoCBillsAPI(api_url, api_key)
    page_offset = 0
    dest_path = fetch_and_store_bills_source_page(
        bills_api=bills_api,
        congress=congress,
        output_location=output_location,
        filesystem=filesystem,
        page_offset=page_offset,
        page_limit=page_limit,
        overwrite=overwrite,
    )
    pagination_data = json.load(filesystem.open(dest_path, "r")).get("pagination")
    total_items = pagination_data.get("count")
    pages = list(range(page_limit, total_items + 1, page_limit))
    logger.info(f"Remaining pages: ({len(pages)=}, {total_items=})")
    for offset in pages:
        _ = fetch_and_store_bills_source_page(
            bills_api=bills_api,
            congress=congress,
            output_location=output_location,
            filesystem=filesystem,
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
    output_location: str,
    filesystem: fsspec.filesystem,
    overwrite: bool,
):
    status = {"present": False}
    if bill_json.get("bill").get(subfield_name):
        url_name = BILL_SUBFIELDS.get(subfield_name)
        logger.debug(f"Subfield present: {subfield_name}")
        status["present"] = True
        subfield_output_path = f"{output_location}{url_name}.json"
        if filesystem.exists(subfield_output_path) and not overwrite:
            status["location"] = subfield_output_path
            status["processed"] = True
            if subfield_name == TEXT_SUBFIELD:
                logger.debug(f"Loading existing subfield: {subfield_output_path}")
                subfield_json = json.load(filesystem.open(subfield_output_path, "r"))
            else:
                logger.debug(f"Skipping existing subfield: {subfield_output_path}")
                return status
        else:
            subfield_json = bills_api.get_bill_subfield(
                congress, house, bill_number, url_name
            )
            json.dump(
                subfield_json, filesystem.open(subfield_output_path, "w"), indent=2
            )
            logger.debug(f"Stored bill subfield JSON: {subfield_output_path}")
            status["location"] = subfield_output_path
            status["processed"] = True
        if subfield_name == TEXT_SUBFIELD:
            status["bill_texts"] = status.get("bill_texts", {})
            for text_version in subfield_json.get("textVersions"):
                for format in text_version.get("formats"):
                    if format.get("type") == "Formatted XML":
                        url = format.get("url")
                        text_file_name = url.split("/")[-1]
                        text_status = status.get("bill_texts", {}).get(
                            text_file_name, {}
                        )
                        bill_text_path = f"{output_location}{text_file_name}"
                        if filesystem.exists(bill_text_path) and not overwrite:
                            text_status["location"] = bill_text_path
                            text_status["processed"] = True
                            logger.debug(
                                f"Skipping existing bill text: {bill_text_path}"
                            )
                        else:
                            bill_text = bills_api.get_bill_text(url)
                            with filesystem.open(bill_text_path, "w") as f_out:
                                f_out.write(bill_text)
                            logger.debug(f"Stored bill text: {bill_text_path}")
                            text_status["location"] = bill_text_path
                            text_status["processed"] = True
                        status["bill_texts"][text_file_name] = text_status
        return status


def fetch_and_store_bill_data(
    bills_api: LoCBillsAPI,
    congress: int,
    house: str,
    bill_number: int,
    output_location: str,
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

    status = {}
    bill_path = f"{congress}/{house}/{bill_number}"
    filesystem, bill_output = init_location(
        f"{output_location}{bill_path}", is_dir=True, is_dest=True
    )
    bill_output_path = f"{bill_output}bill.json"
    if filesystem.exists(bill_output_path) and not overwrite:
        logger.debug(f"Loading existing: {bill_output_path}")
        bill_json = json.load(filesystem.open(bill_output_path, "r"))
        status["bill"] = {"processed": True, "location": bill_output_path}
    else:
        bill_json = bills_api.get_bill(congress, house, bill_number)
        json.dump(bill_json, filesystem.open(bill_output_path, "w"), indent=2)
        logger.debug(f"Stored base bill JSON: {bill_output_path}")
        status["bill"] = {"processed": True, "location": bill_output_path}
    status["subfields"] = status.get("subfields", {})
    for subfield_name in BILL_SUBFIELDS.keys():
        subfield_status = fetch_and_store_subfield_data(
            bills_api=bills_api,
            congress=congress,
            house=house,
            bill_number=bill_number,
            subfield_name=subfield_name,
            bill_json=bill_json,
            output_location=bill_output,
            filesystem=filesystem,
            overwrite=overwrite,
        )
        status["subfields"][subfield_name] = subfield_status
    return status


def fetch_and_store_bills_from_source_page(
    api_url: str,
    api_key: str,
    source_file: str,
    output_location: str,
    overwrite: bool,
):

    source_filesystem, source_file = init_location(source_file)
    dest_filesystem, output_location = init_location(
        output_location, is_dir=True, is_dest=True
    )

    source_status_file = source_file.replace(".json", ".status.json")

    source_data = json.load(source_filesystem.open(source_file, "r"))
    status_data = json.load(source_filesystem.open(source_status_file, "r"))

    bills_api = LoCBillsAPI(api_url, api_key)
    page_bills = source_data.get("bills")
    total_bills = len(page_bills)
    for count, bill_data in enumerate(source_data.get("bills"), start=1):
        logger.info(f"{count}/{total_bills}")
        congress = int(bill_data.get("congress"))
        house = bill_data.get("type").lower()
        bill_number = int(bill_data.get("number"))
        bill_path = f"{congress}/{house}/{bill_number}"
        bill_status = fetch_and_store_bill_data(
            bills_api=bills_api,
            congress=congress,
            house=house,
            bill_number=bill_number,
            output_location=output_location,
            overwrite=overwrite,
        )
        status_data["bills"][bill_path] = bill_status
        json.dump(
            status_data, source_filesystem.open(source_status_file, "w"), indent=2
        )


def fetch_and_store_congress_bills(
    api_url: str,
    api_key: str,
    congress: int,
    source_location: str,
    output_location: str,
    overwrite: bool,
):
    source_filesystem, source_dir = init_location(source_location, is_dir=True)

    source_pages = source_filesystem.glob(f"{source_dir}{congress}_*.json")

    for page in source_pages:
        if not page.endswith("status.json"):
            s3_page_uri = f"s3://{page}"
            fetch_and_store_bills_from_source_page(
                api_url=api_url,
                api_key=api_key,
                source_file=s3_page_uri,
                output_location=output_location,
                overwrite=overwrite,
            )
