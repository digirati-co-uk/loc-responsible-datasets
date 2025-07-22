# 03_Assembly

The script assumes that the transcripts for the audio files have already been created using the script in [01_transcription](../01_transcription) and the annotations have been added using [02_annotation](../02_annotation).

### Script explanations

Generates CSV and XML files. For the CSV files a column will contain a link to the audio files (at a URL).

## How to run

Activate suitable environment. If using a uv venv, run `uv run <script_name.py>` with suitable arguments if not already edited in the code.

The arguments are:

* json_root: Location of the annotated JSON files to process.
* output_directory: Location of the output files.
* audio_root: Location of the audio files.
* destination_url_base: Base URL for the audio files in the output CSV and XML files.
* log_level

To run:

`uv run 03_run_assembly.py --json-root=../../local_data/04_speech_to_text/source_txt/ --output-directory=../../local_data/04_speech_to_text/output/ --audio-root=../../local_data/04_speech_to_text/source_audio/ --destination-url-base=https://example.org/speech-to-text/`

For help. run:

`uv run 03_run_assembly.py --help`




