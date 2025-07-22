# 01_Transcription
This directory holds the code for transcribing audio files using Whisper (currently the code assumes MLX) and saving as JSON.

## How to run

Activate suitable environment. If using a uv venv, run `uv run <script_name.py>` with suitable arguments if not already edited in the code.

The arguments are:

* audio_root: the directory where the audio files are located
* txt_file_dir: the directory where the Whisper transcript files will be stored
* log_level

To run:

`uv run 01_transcriber.py --audio-root=../../local_data/04_speech_to_text/source_audio/ --txt-file-dir=../../local_data/04_speech_to_text/source_txt/`

For help. run:

`uv run 01_transcriber.py --help`




