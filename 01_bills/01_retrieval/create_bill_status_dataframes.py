#!/usr/bin/env python3

import typer
import logging

from typing_extensions import Annotated
from pathlib import Path

from utils.status import (
    congress_bill_status_dataframes,
)


def create_bill_status_dataframes(
    source_location: Annotated[
        str,
        typer.Option(
            help="Location containing source pages and source bills created by other scripts."
        ),
    ] = "s3://loc-responsible-datasets-source-data/01_bills/",
    output_location: Annotated[
        str, typer.Option(help="Location to store the generated dataframes.")
    ] = "./reports/bills/",
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

    congress_bill_status_dataframes(
        source_location=source_location,
        output_location=output_location,
    )


if __name__ == "__main__":
    typer.run(create_bill_status_dataframes)
