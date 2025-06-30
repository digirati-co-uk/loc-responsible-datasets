import shutil
from glob import glob
import pandas as pd
from pathlib import Path
import urllib.parse
import shutil
import os

json_root = "../../../local_data/04_speech_to_text/source_txt/"
audio_root = "../../../local_data/04_speech_to_text/source_audio/"
destination = "/Users/matt.mcgrattan/code/lrd-speech-to-text/docs"


def convert_json_to_csv(json_file, output_directory):
    """
    Convert a JSON file to a CSV file.
    :param json_file: Path to the input JSON file.
    :param output_directory: Path to the output CSV file.
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
        web_audio_url = f"https://digirati-co-uk.github.io/lrd-speech-to-text/{'/'.join(web_audio_filepath.parts[-3:])}"
        with open(json_file, "r", encoding="utf-8") as f:
            data = pd.read_json(f)

        # Split the iob column into separate columns,
        # the column contains either an O or a B-XXX, I-XXX, L-XXX, U-XXX
        iob_columns = data["iob"].str.split("-", expand=True)
        iob_columns.columns = ["iob", "entity_type"]
        # Combine the original data with the new iob columns
        # and drop the original iob column
        data = data.drop(columns=["iob", "bilou"])
        data = pd.concat([data, iob_columns], axis=1)
        # reorder the columns so that text is first, then io, then entity_type
        # then start_time and end_time
        data = data[["text", "iob", "entity_type", "start_time", "end_time"]]
        # add the web audio URL to the data
        # for every row, add a new column with the web audio URL
        # which has the value of web_audio_url + the start_time in seconds
        # i.e. web_audio_url + "#t=start_time"
        data["audio_url"] = web_audio_url + "#t=" + data["start_time"].astype(str)
        # save the data to a CSV file
        web_file_path.parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(web_file_path, index=False, encoding="utf-8")
        # copy the audio file to the web_audio_filepath
        # copy the audio_file to the web_audio_filepath
        if not os.path.exists(web_audio_filepath.parent):
            web_audio_filepath.parent.mkdir(parents=True, exist_ok=True)
        if not os.path.exists(web_audio_filepath):
            # Copy the audio file to the web directory
            print(f"Copying {audio_file} to {web_audio_filepath}")
            shutil.copy2(audio_file, web_audio_filepath)




if __name__ == "__main__":
    json_files = glob(json_root + "**/*annotated.json", recursive=True)
    curran = [x for x in json_files if "curran" in x.lower()]
    for json_file in json_files:
        convert_json_to_csv(json_file, destination)
