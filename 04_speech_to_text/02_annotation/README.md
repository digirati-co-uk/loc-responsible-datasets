# 02_Annotation
This directory holds the code for enriching the existing transcript files (in Whisper JSON format) with entities and reformatting to the intermediate JSON format.

The script assumes that the transcripts for the audio files have already been created using the script in [01_transcription](../01_transcription).

### Script explanations
`02_run_annotator.py` parses the Whisper transcript files and uses Spacy to annotate the transcript with entities of types:

* PERSON 
* ORG 
* GPE 
* LOC 
* FAC 
* NORP 
* DATE 
* EVENT
* QUANTITY

## How to run

Activate suitable environment. If using a uv venv, run `uv run <script_name.py>` with suitable arguments if not already edited in the code.

The arguments are:

* txt_file_dir: the directory where the existing Whisper transcript files are stored and where the annotated files will be written.
* log_level

To run:

`uv run 02_run_annotator.py --txt-file-dir=../../local_data/04_speech_to_text/source_txt/`

For help. run:

`uv run 02_run_annotator.py --help`




