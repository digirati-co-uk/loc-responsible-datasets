import typer
import logging
from tqdm import tqdm
from pathlib import Path
from typing_extensions import Annotated

from utils.annotate import annotate_transcription


def apply_annotator(
    txt_file_dir: Annotated[
        Path, typer.Option(help="Location to save the text transcripts to.")
    ] = Path("../../local_data/04_speech_to_text/source_txt/"),
    log_level: Annotated[
        str,
        typer.Option(
            help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
        ),
    ] = "INFO",
):
    """
    Converts audio files to text and saves the transcripts to the specified directory.

    In typical usage the `txt_file_dir` is for intermediate storage of text files
    before they are annotated with entity metadata. The `log_level` can be set to control
    the verbosity of the logging output. Valid levels are DEBUG, INFO, WARNING, ERROR, etc.

    Args:
        txt_file_dir (Path): The directory where the text transcripts are saved (as Whisper files), and the
            JSON annotated files will be stored.
        log_level (str): The logging level to set for the application.
    Raises:
        typer.BadParameter: If the provided log level is invalid.
    """
    log_level = log_level.upper()
    level_enum = getattr(logging, log_level, None)
    if not isinstance(level_enum, int):
        raise typer.BadParameter(f"Invalid log level: {log_level}")
    logging.basicConfig(
        level=level_enum,
        format="%(asctime)s - %(name)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s",
    )
    json_files = list(
        txt_file_dir.rglob("*.json")
    )  # Adjust the file extension as needed
    json_files = [j for j in json_files if not j.name.endswith("_annotated.json")]
    for file in tqdm(json_files):
        grandparent_dir = file.parent.parent.name
        parent_dir = file.parent.name
        json_output_path = (
            txt_file_dir
            / grandparent_dir
            / parent_dir
            / (file.stem + "_annotated.json")
        )
        # Call the annotator function
        annotate_transcription(json_file=file, output_file=json_output_path)


if __name__ == "__main__":
    typer.run(apply_annotator)
