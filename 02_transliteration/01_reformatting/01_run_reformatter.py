import typer
import logging

from pathlib import Path
from typing_extensions import Annotated

from utils.reformatter import convert_txt_to_xml


def apply_reformatter(
    txt_file_path: Annotated[
        Path, typer.Option(help="Location to load in TXT dataset from.")
    ] = Path(
        "../../local_data/02_transliteration/Japanese_records_personal_names_w_800_20250325.txt"
    ),
    xml_file_dir: Annotated[
        Path, typer.Option(help="Location to save in MARC XML dataset to.")
    ] = Path("../../local_data/02_transliteration/source_xml/"),
    log_level: Annotated[
        str,
        typer.Option(
            help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
        ),
    ] = "INFO",
):
    """
    Converts TXT file to MARCXML and saves to output dir under same file name
    """
    log_level = log_level.upper()
    level_enum = getattr(logging, log_level, None)
    if not isinstance(level_enum, int):
        raise typer.BadParameter(f"Invalid log level: {log_level}")
    logging.basicConfig(
        level=level_enum,
        format="%(asctime)s - %(name)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s",
    )

    xml_file_name = txt_file_path.with_suffix(".xml").name
    output_path = xml_file_dir / xml_file_name

    convert_txt_to_xml(txt_input_path=txt_file_path, xml_output_path=output_path)


if __name__ == "__main__":
    typer.run(apply_reformatter)
