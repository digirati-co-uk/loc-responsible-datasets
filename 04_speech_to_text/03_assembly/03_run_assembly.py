import typer
import logging
from tqdm import tqdm
from glob import glob
from pathlib import Path
from typing_extensions import Annotated

from utils.convert_to_csv import convert_json_to_csv, convert_json_to_xml


def apply_assembly(
    json_root: Annotated[
        Path, typer.Option(help="Location of the annotated JSON files to process.")
    ] = Path("../../local_data/04_speech_to_text/source_txt/"),
    output_directory: Annotated[
            Path, typer.Option(help="Location of the output files.")
        ] = Path("../../local_data/04_speech_to_text/output/"),
    audio_root: Annotated[
        Path, typer.Option(help="Location of the audio files.")
    ] = Path("../../local_data/04_speech_to_text/source_audio/"),
    destination_url_base: Annotated[
        str,
        typer.Option(
            help="Base URL for the audio files in the output CSV and XML files."
        ),
    ] = "https://digirati-co-uk.github.io/lrd-speech-to-text/",
    log_level: Annotated[
        str,
        typer.Option(
            help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
        ),
    ] = "INFO",
):
    """
    Assembles the text transcripts into CSV and XML files. Adds audio file links
    and copies the audio files to the output directory.


    """
    log_level = log_level.upper()
    level_enum = getattr(logging, log_level, None)
    if not isinstance(level_enum, int):
        raise typer.BadParameter(f"Invalid log level: {log_level}")
    logging.basicConfig(
        level=level_enum,
        format="%(asctime)s - %(name)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s",
    )
    json_files = glob(str(json_root / "**/*annotated.json"), recursive=True)
    for json_file in tqdm(json_files):
        convert_json_to_csv(
            json_file=json_file,
            output_directory=output_directory,
            audio_root=audio_root,
            destination_url_base=destination_url_base,
        )
        convert_json_to_xml(json_file=json_file, output_directory=output_directory)


if __name__ == "__main__":
    typer.run(apply_assembly)
