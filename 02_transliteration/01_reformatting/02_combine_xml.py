import typer
import logging

from pathlib import Path
from typing_extensions import Annotated

from utils.reformatter import parse_marc_xml, convert_list_to_marcxml


def combine_xml(
    xml_file_path_1: Annotated[
        Path, typer.Option(help="Location to load in first MARCXML dataset from.")
    ] = Path(
        "../../local_data/02_transliteration/source_xml/Japanese_records_personal_names_w_800_20250325.xml"
    ),
    xml_file_path_2: Annotated[
        Path, typer.Option(help="Location to load in second MARCXML dataset to.")
    ] = Path(
        "../../local_data/02_transliteration/source_xml/Japanese_records_w_880_20250314.xml"
    ),
    combined_xml_output_path: Annotated[
        Path, typer.Option(help="Location to save in MARC XML dataset to.")
    ] = Path(
        "../../local_data/02_transliteration/source_xml/all_unique_Japanese_records.xml"
    ),
    log_level: Annotated[
        str,
        typer.Option(
            help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
        ),
    ] = "INFO",
):
    """
    Loads in two MARCXML files, combines and saves a singular XML file.
    """
    log_level = log_level.upper()
    level_enum = getattr(logging, log_level, None)
    if not isinstance(level_enum, int):
        raise typer.BadParameter(f"Invalid log level: {log_level}")
    logging.basicConfig(
        level=level_enum,
        format="%(asctime)s - %(name)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s",
    )

    xml_list_1 = parse_marc_xml(xml_file_path_1)
    xml_list_2 = parse_marc_xml(xml_file_path_2)

    convert_list_to_marcxml(xml_list_1 + xml_list_2, combined_xml_output_path)


if __name__ == "__main__":
    typer.run(combine_xml)
