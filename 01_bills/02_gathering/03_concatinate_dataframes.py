import typer
import logging

from pathlib import Path
from typing_extensions import Annotated
from utils.dataframe import (
    concat_dataframes,
)

import pandas as pd


def get_concatinated_dataframe(
    source_directory: Annotated[
        Path,
        typer.Option(
            help="Location to retrieve source dataframes separated by congress."
        ),
    ] = Path("../../local_data/01_bills/generated_data"),
    dataframe_file: Annotated[
        str,
        typer.Option(help="Name of consistent dataframe file for filtering."),
    ] = "compiled_subjects.csv.gz",
    log_level: Annotated[
        str,
        typer.Option(
            help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITIAL)"
        ),
    ] = "INFO",
):
    """
    Used for when 01 or 02 is run on a Congress by Congress basis.
    Runs through dataframe_file CSVs in source directory and reads in the data.
    Concatinates dataframe and saves to source directory under the file name "concat_<dataframe_file>"
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

    concat_dataframes(source_directory=source_directory, dataframe_file=dataframe_file)


if __name__ == "__main__":
    typer.run(get_concatinated_dataframe)
