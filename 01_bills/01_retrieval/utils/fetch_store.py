import json
import logging
import typing
from pathlib import Path

import fsspec

from .api import (
    LoCBillsAPI,
    BILL_SUBFIELDS,
    TEXT_SUBFIELD,
    TEXT_TYPES,
)
from .location import (
    init_location,
)
from .status import (
    is_bill_processed,
    is_page_processed,
)

logger = logging.getLogger(__name__)

logger = logging.getLogger("ray")
logger.setLevel(logging.INFO)


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
            try:
                subfield_json = bills_api.get_bill_subfield(
                    congress, house, bill_number, url_name
                )
                json.dump(
                    subfield_json, filesystem.open(subfield_output_path, "w"), indent=2
                )
                logger.debug(f"Stored bill subfield JSON: {subfield_output_path}")
                status["location"] = subfield_output_path
                status["processed"] = True
            except Exception as e:
                status["processed"] = False
                status["exception"] = str(e)
                logger.info(f"Bill subfield error: ({url_name}, {str(e)})")
                return status
        if subfield_name == TEXT_SUBFIELD:
            status["bill_texts"] = status.get("bill_texts", {})
            for text_version in subfield_json.get("textVersions"):
                for format in text_version.get("formats"):
                    if format.get("type").strip() in TEXT_TYPES:
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
                            try:
                                bill_text = bills_api.get_bill_text(url)
                                with filesystem.open(bill_text_path, "w") as f_out:
                                    f_out.write(bill_text)
                                logger.debug(f"Stored bill text: {bill_text_path}")
                                text_status["location"] = bill_text_path
                                text_status["processed"] = True
                            except Exception as e:
                                text_status["processed"] = False
                                text_status["exception"] = str(e)
                                logger.info(
                                    f"Bill text error: ({bill_text_path}, {str(e)})"
                                )

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
    status["subfields"] = status.get("subfields", {})
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
        try:
            bill_json = bills_api.get_bill(congress, house, bill_number)
            json.dump(bill_json, filesystem.open(bill_output_path, "w"), indent=2)
            logger.debug(f"Stored base bill JSON: {bill_output_path}")
            status["bill"] = {"processed": True, "location": bill_output_path}
        except Exception as e:
            logger.info(f"Bill error: ({bill_output_path}, {str(e)})")
            status["bill"] = {"processed": False, "exception": str(e)}
            return status
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
    status_data: dict = {},
):

    source_filesystem, source_file = init_location(source_file)
    dest_filesystem, output_location = init_location(
        output_location, is_dir=True, is_dest=True
    )
    logger.info(f"Processing page: {source_file}")
    source_data = json.load(source_filesystem.open(source_file, "r"))
    source_status_file = source_file.replace(".json", ".status.json")
    if not status_data:
        status_data = json.load(source_filesystem.open(source_status_file, "r"))

    bills_api = LoCBillsAPI(api_url, api_key)
    page_bills = source_data.get("bills")
    total_bills = len(page_bills)
    for count, bill_data in enumerate(source_data.get("bills"), start=1):
        logger.debug(f"{count}/{total_bills}")
        congress = int(bill_data.get("congress"))
        house = bill_data.get("type").lower()
        bill_number = int(bill_data.get("number"))
        bill_path = f"{congress}/{house}/{bill_number}"

        if (
            not is_bill_processed(status_data.get("bills", {}).get(bill_path))
            or overwrite
        ):
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
        else:
            logger.info(f"Bill already processed: {bill_path}")


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


def fetch_and_store_congress_bills_by_status(
    api_url: str,
    api_key: str,
    congress: int,
    source_location: str,
    output_location: str,
    overwrite: bool,
):
    source_filesystem, source_dir = init_location(source_location, is_dir=True)
    source_pages = source_filesystem.glob(f"{source_dir}{congress}_*.json")

    status_pages = filter(lambda x: x.endswith("status.json"), source_pages)
    for page in status_pages:

        source_page = page.replace(".status.json", ".json")
        status_data = json.load(source_filesystem.open(page, "r"))
        if is_page_processed(status_data):
            logger.info(f"Skipping processed page: {source_page}")
        else:
            s3_page_uri = f"s3://{source_page}"
            fetch_and_store_bills_from_source_page(
                api_url=api_url,
                api_key=api_key,
                source_file=s3_page_uri,
                output_location=output_location,
                overwrite=overwrite,
                status_data=status_data,
            )


def update_source_pages_subfield_processed_status(
    congress: int,
    subfield: str,
    subfield_status: bool,
    source_location: str,
):
    source_filesystem, source_dir = init_location(source_location, is_dir=True)
    status_pages = source_filesystem.glob(f"{source_dir}{congress}_*.status.json")
    for page in status_pages:
        logger.info(f"Updating status {subfield}={subfield_status} in {page}")
        status_data = json.load(source_filesystem.open(page, "r"))
        updates = []
        for bill_key, status in status_data.get("bills").items():
            if subfield_data := status.get("subfields", {}).get(subfield):
                updates.append(bill_key)
        for bill_key in updates:
            status_data["bills"][bill_key]["subfields"][subfield][
                "processed"
            ] = subfield_status
        json.dump(status_data, source_filesystem.open(page, "w"), indent=2)
