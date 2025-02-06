#!/usr/bin/env python3

import typer
import logging

from typing_extensions import Annotated
from pathlib import Path
from utils.fetch_store import (
    fetch_and_store_congress_bills_source_pages,
)


def get_congress_bills_source_pages(
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
    congress: Annotated[
        int, typer.Option(help="Congress to fetch and store bill pages for")
    ] = 111,
    output_directory: Annotated[
        Path, typer.Option(help="Location to store the pages fetched from the API.")
    ] = Path("../local_data/source_pages"),
    page_limit: Annotated[
        int, typer.Option(help="Number of bills in each page, max: 250")
    ] = 250,
    overwrite: Annotated[
        bool,
        typer.Option(help="Whether to refetch data and overwrite an existing page"),
    ] = False,
    log_level: Annotated[
        str,
        typer.Option(
            help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
        ),
    ] = "INFO",
):
    """
    Local CLI Wrapper for the `fetch_and_store_congress_bills_source_pages` function.

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

    fetch_and_store_congress_bills_source_pages(
        api_url=api_url,
        api_key=api_key,
        congress=congress,
        output_directory=output_directory,
        page_limit=page_limit,
        overwrite=overwrite,
    )


if __name__ == "__main__":
    typer.run(get_congress_bills_source_pages)
