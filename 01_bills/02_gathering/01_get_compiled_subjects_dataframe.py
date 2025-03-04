import typer
import logging

from pathlib import Path
from typing_extensions import Annotated
from utils.dataframe import fetch_and_populate_subject_dataframe_from_source_data

import pandas as pd


def get_compiled_subjects_dataframe(
    source_directory: Annotated[
        Path,
        typer.Option(help="Location to retrieve source data fetched from the API."),
    ] = Path("../../local_data/01_bills/source_bills"),
    output_path: Annotated[
        Path,
        typer.Option(help="Location to dataframe created."),
    ] = Path("../../local_data/01_bills/generated_data/full_compiled_subjects.csv.gz"),
    log_level: Annotated[
        str,
        typer.Option(
            help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITIAL)"
        ),
    ] = "INFO",
):
    """
    Runs through all subject.json within a directory
    Pulls out bill identifiers, legislativeSubjects and policyArea to populate a dataframe
    Saves dataframe to output path
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

    fetch_and_populate_subject_dataframe_from_source_data(
        source_directory=source_directory, output_path=output_path
    )


if __name__ == "__main__":
    typer.run(get_compiled_subjects_dataframe)
