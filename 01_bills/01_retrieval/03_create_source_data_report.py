#!/usr/bin/env python3

import typer
import logging

from typing_extensions import Annotated
from pathlib import Path

# from utils.fetch_store import (
#     fetch_and_store_bills_from_source_page,
# )


def source_data_report(
    source_directory: Path,
    output_directory: Path,
):
    pages_dir = source_directory / "source_pages"
    bills_dir = source_directory / "source_bills"
    for page_path in pages_dir.glob("*.json"):
        print(page_path)


def create_source_data_report(
    source_directory: Annotated[
        Path,
        typer.Option(
            help="Location containing `source_bills` and `source_pages` directories created by other scripts."
        ),
    ] = Path("../local_data/"),
    output_directory: Annotated[
        Path, typer.Option(help="Location to store the generated report.")
    ] = Path("../local_data/"),
    log_level: Annotated[
        str,
        typer.Option(
            help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
        ),
    ] = "INFO",
):
    """
    Local CLI Wrapper for the `source_data_report` function.

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

    source_data_report(
        source_directory=source_directory,
        output_directory=output_directory,
    )


if __name__ == "__main__":
    typer.run(create_source_data_report)
