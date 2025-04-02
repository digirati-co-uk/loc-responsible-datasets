import typer
import logging

from utils.assembler import (
    assemble_transliteration_df,
)  # Assembler, load_variable_from_file
from pathlib import Path
from typing_extensions import Annotated

import pandas as pd

FILTER_ON = {
    "no_filters": {},
    "personal_names": {"100": ["a"], "600": ["a"], "700": ["a"], "800": ["a"]},
    "corporate_names": {"110": ["a"], "610": ["a"], "710": ["a"], "810": ["a"]},
}

TO_EXCLUDE = {
    "no_names": [
        "100",
        "110",
        "600",
        "610",
        "700",
        "710",
        "800",
        "810",
    ],
}


def apply_assembly(
    xml_file_path: Annotated[
        Path, typer.Option(help="Location to load in MARC XML dataset from.")
    ] = Path(
        "../../local_data/02_transliteration/source_xml/Japanese_records_personal_names_w_800_20250325.xml"
    ),
    output_dir: Annotated[
        Path, typer.Option(help="Directory to save resulting dataframe.")
    ] = Path("../../local_data/02_transliteration/generated_data/"),
    filtering_type: Annotated[
        str,
        typer.Option(
            help="Type of filtering to be applied to original dataset (no_filters, personal_names, corporate_names)"
        ),
    ] = "no_filters",
    excluding_type: Annotated[
        str,
        typer.Option(
            help="Fields to be excluded from the original dataset (None, no_names)"
        ),
    ] = None,
    log_level: Annotated[
        str,
        typer.Option(
            help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
        ),
    ] = "INFO",
):
    """
    Takes a MARCXML file.
    Pulls out transliterated field (880) and pairs them
    Creates dataframe according to reformatter_type
    Save dataframe to output directory
    """
    log_level = log_level.upper()
    level_enum = getattr(logging, log_level, None)
    if not isinstance(level_enum, int):
        raise typer.BadParameter(f"Invalid log level: {log_level}")
    logging.basicConfig(
        level=level_enum,
        format="%(asctime)s - %(name)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s",
    )

    if excluding_type:
        to_exclude = TO_EXCLUDE.get(excluding_type)
    else:
        to_exclude = []

    transliteration_df = assemble_transliteration_df(
        file_path=xml_file_path,
        filter_on=FILTER_ON.get(filtering_type),
        to_exclude=to_exclude,
    )

    file_name = xml_file_path.stem

    if to_exclude:
        output_path = (
            output_dir
            / f"transliteration_{file_name}_{filtering_type}_{excluding_type}.csv.gz"
        )
    else:
        output_path = (
            output_dir / f"transliteration_{file_name}_{filtering_type}.csv.gz"
        )

    print(f"Saving to: {output_path=} ...")
    transliteration_df.to_csv(output_path, compression="gzip", index=False)


if __name__ == "__main__":
    typer.run(apply_assembly)
