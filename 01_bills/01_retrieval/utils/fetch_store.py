import json
import logging

from pathlib import Path

from .api import (
    LoCBillsAPI,
)

logger = logging.getLogger(__name__)


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
    if dest_path.exists():
        logger.debug(f"Page JSON already present: ({dest_path=})")
        if not overwrite:
            return dest_path
        else:
            logger.debug(f"Overwriting: ({dest_path=})")
    source_page_json = bills_api.get_congress_bills_page(
        congress=congress, page_offset=page_offset, page_limit=page_limit
    )
    json.dump(source_page_json, dest_path.open("w"), indent=2)
    logger.debug(f"Stored page JSON: ({dest_path=})")
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
