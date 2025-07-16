from glob import glob
import pandas as pd
from pathlib import Path
import urllib.parse
import shutil
import os
import string
import logging

logger = logging.getLogger(__name__)


def convert_json_to_csv(
    json_file,
    output_directory,
    audio_root,
    destination_url_base="https://digirati-co-uk.github.io/lrd-speech-to-text/",
):
    """
    Convert a JSON file to a CSV file.

    The file will include a column for the audio URL, which is constructed
    on top of the `destination_url_base` and the relative path to the audio file.

    The audio file will be copied to the output directory, maintaining the
    directory structure relative to the `json_file` location.

    :param json_file: Path to the input JSON file.
    :param output_directory: Path to the output CSV file.
    :param audio_root: Path to the root directory of the audio files.
    :param destination_url_base: Base URL for the destination where the audio files will be hosted.
    """

    # Create a filename for the output CSV file
    file_root = [p.name for p in Path(json_file).parents][1::-1]
    output_file = (
        Path(output_directory)
        / file_root[0]
        / file_root[1]
        / Path(json_file).with_suffix(".csv").name
    )
    web_file_path = Path(
        urllib.parse.quote(str(output_file).replace(" ", "_"), safe="/")
    )
    audio_source = (
        Path(audio_root)
        / file_root[0]
        / file_root[1]
        / Path(json_file).name.replace("_annotated.json", "*")
    )
    # glob for the audio file that matches audio_source
    # Find the first matching audio file (.wav, .mp3, or .m4a) case-insensitively
    audio_file = next(
        (
            f
            for f in glob(str(audio_source), recursive=True)
            if f.lower().endswith((".mp3"))
        ),
        None,
    )
    if audio_file:
        web_audio_filepath = Path(
            urllib.parse.quote(
                str(web_file_path.parent / Path(audio_file).name).replace(" ", "_"),
                safe="/",
            )
        )

        # Load the JSON datasets.g
        web_audio_url = (
            f"{destination_url_base}/{'/'.join(web_audio_filepath.parts[-3:])}"
        )
        with open(json_file, "r", encoding="utf-8") as f:
            data = pd.read_json(f)

        # Split the iob column into separate columns,
        iob_columns = data["iob"].str.split("-", expand=True)
        iob_columns.columns = ["iob", "entity_type"]
        # Combine the original data with the new iob columns
        # and drop the original iob column
        data = data.drop(columns=["iob", "bilou"])
        data = pd.concat([data, iob_columns], axis=1)
        # reorder the columns
        data = data[["text", "iob", "entity_type", "start_time", "end_time"]]
        # add the web audio URL to the data + "#t=start_time"
        data["audio_url"] = web_audio_url + "#t=" + data["start_time"].astype(str)
        # save the data to a CSV file
        web_file_path.parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(web_file_path, index=False, encoding="utf-8")
        # copy the audio file to the web_audio_filepath
        if not os.path.exists(web_audio_filepath.parent):
            web_audio_filepath.parent.mkdir(parents=True, exist_ok=True)
        if not os.path.exists(web_audio_filepath):
            # Copy the audio file to the web directory
            logger.debug(f"Copying {audio_file} to {web_audio_filepath}")
            shutil.copy2(audio_file, web_audio_filepath)


def convert_json_to_xml(json_file, output_directory):
    """
    Convert a JSON file to an XML file.
    :param json_file: Path to the input JSON file.
    :param output_directory: Path to the output XML file.
    """
    # Create a filename for the output CSV file
    file_root = [p.name for p in Path(json_file).parents][1::-1]
    output_file = (
        Path(output_directory)
        / file_root[0]
        / file_root[1]
        / Path(json_file).with_suffix(".xml").name
    )
    web_file_path = Path(
        urllib.parse.quote(str(output_file).replace(" ", "_"), safe="/")
    )
    # Split the iob column into separate columns,
    # the column contains either an O or a B-XXX, I-XXX, L-XXX, U-XXX
    with open(json_file, "r", encoding="utf-8") as f:
        data = pd.read_json(f)
    iob_columns = data["iob"].str.split("-", expand=True)
    iob_columns.columns = ["iob", "entity_type"]
    # remove iob from this iob_columns
    iob_columns = iob_columns.drop(columns=["iob"])
    data = pd.concat([data, iob_columns], axis=1)
    # Convert to XML
    entity_text = []
    current_entity = None

    for index, row in data.iterrows():
        iob_value = row["iob"]
        if iob_value.startswith("B-"):
            if (
                current_entity
            ):  # N.B. if a current entity already exists, current_text will not be empty
                entity_text.append(
                    f"<{current_entity}>{' '.join(current_text)}</{current_entity}>"
                )
            current_entity = row["entity_type"]
            current_text = [row["text"]]
        elif iob_value.startswith("I-") and current_entity == row["entity_type"]:
            current_text.append(row["text"])
        else:
            if current_entity:
                entity_text.append(
                    f"<{current_entity}>{' '.join(current_text)}</{current_entity}>"
                )
                current_entity = None
            entity_text.append(row["text"])

    if current_entity:
        entity_text.append(
            f"<{current_entity}>{' '.join(current_text)}</{current_entity}>"
        )
    # Save the XML file concatenate the text column into a single string
    # separated by spaces and wrapped in a root tag. N.B.
    # no specific namespace is used, so this is a simple XML file.
    xml_content = "<TRANSCRIPTION>\n"
    xml_content += " ".join(entity_text)
    # Normalize whitespace, by replacing spces before punctuation
    # but do not replace spaces before < or > as these are XML tags
    for punct in string.punctuation:
        if punct not in ["<", ">"]:
            xml_content = xml_content.replace(f" {punct}", punct)
    xml_content = xml_content.replace(" n't", "n't").replace(" 's", "'s")
    xml_content += "\n</TRANSCRIPTION>"
    with open(web_file_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
