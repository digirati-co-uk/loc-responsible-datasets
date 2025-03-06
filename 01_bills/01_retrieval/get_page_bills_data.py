#!/usr/bin/env python3

import typer
import logging

from typing_extensions import Annotated
from pathlib import Path
from utils.fetch_store import (
    fetch_and_store_bills_from_source_page,
)


def get_bills_from_source_page(
    api_key: Annotated[
        str,
        typer.Argument(
            help="API key for the Congress.gov API instance",
            envvar="CONGRESS_GOV_API_KEY",
        ),
    ],
    api_url: Annotated[
        str, typer.Option(help="Base url for the Congress.gov API instance.")
    ] = "https://api.congress.gov/v3/",
    source_file: Annotated[
        str,
        typer.Option(
            help="Location of JSON file containing the source page with list of bills. Can be a s3 url (e.g. s3://loc-responsible-datasets-source-data/01_bills/source_pages/111_0.json) or a directory path."
        ),
    ] = "../local_data/01_bills/source_pages/111_0.json",
    output_location: Annotated[
        str,
        typer.Option(
            help="Location to store the bill data fetched from the API. Can be a s3 url (e.g. s3://loc-responsible-datasets-source-data/01_bills/source_bills) or a directory path."
        ),
    ] = "../local_data/01_bills/source_bills",
    overwrite: Annotated[
        bool,
        typer.Option(help="Whether to refetch data and overwrite existing bill files"),
    ] = False,
    log_level: Annotated[
        str,
        typer.Option(
            help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
        ),
    ] = "INFO",
):
    """
    Local CLI Wrapper for the `fetch_and_store_bills_from_source_page` function.

    """
    log_level = log_level.upper()
    level_enum = getattr(logging, log_level, None)
    if not isinstance(level_enum, int):
        raise typer.BadParameter(f"Invalid log level: {log_level}")
    logging.basicConfig(
        level=level_enum,
        format="%(asctime)s - %(name)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s",
    )
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("charset_normalizer").setLevel(logging.WARNING)

    fetch_and_store_bills_from_source_page(
        api_url=api_url,
        api_key=api_key,
        source_file=source_file,
        output_location=output_location,
        overwrite=overwrite,
    )


if __name__ == "__main__":
    typer.run(get_bills_from_source_page)
