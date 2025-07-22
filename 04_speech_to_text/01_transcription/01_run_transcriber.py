import typer
import logging
from tqdm import tqdm
from pathlib import Path
from typing_extensions import Annotated

from utils.convert_audio_to_text import convert_audio_to_text

def apply_transcriber(
    audio_root: Annotated[
        Path, typer.Option(help="Location to load in audio files from. Will search recursively.")
    ] = Path(
        "../../local_data/04_speech_to_text/source_audio/"
    ),
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
    """
    log_level = log_level.upper()
    level_enum = getattr(logging, log_level, None)
    if not isinstance(level_enum, int):
        raise typer.BadParameter(f"Invalid log level: {log_level}")
    logging.basicConfig(
        level=level_enum,
        format="%(asctime)s - %(name)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s",
    )
    # Get all files and filter for audio files (case insensitive)
    all_files = list(audio_root.rglob("*.*"))
    audio_files = [f for f in all_files if f.suffix.lower() in ('.mp3') and "DS_Store" not in f.name]
    # Just process the MP3s as there were some WAVs which were converted to MP3s already
    # so reprocessing them would be redundant.
    for file in tqdm(audio_files):
        txt_file_name = file.with_suffix(".txt").name
        json_file_name = file.with_suffix(".json").name
        grandparent_dir = file.parent.parent.name
        parent_dir = file.parent.name
        # replace any spaces in the filename with underscores
        txt_file_name = txt_file_name.replace(" ", "_")
        txt_output_path = txt_file_dir /grandparent_dir/ parent_dir / txt_file_name
        json_output_path = txt_file_dir / grandparent_dir / parent_dir / json_file_name
        convert_audio_to_text(file, textfile_path=txt_output_path, jsonfile_path=json_output_path)

if __name__ == "__main__":
    typer.run(apply_transcriber)