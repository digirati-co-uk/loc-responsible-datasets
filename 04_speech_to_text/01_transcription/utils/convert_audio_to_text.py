import mlx_whisper
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)


def convert_audio_to_text(audio_file_path: Path ,
                          textfile_path: Path,
                          jsonfile_path: Path,
                          model="mlx-community/whisper-large-v3-turbo"):
    """
    Convert audio file to text using the specified model.

    Args:
        audio_file_path (str): Path to the audio file.
        model: The model to use for transcription.

    Returns:
        str: Transcribed text from the audio file.
    """
    try:
        result = mlx_whisper.transcribe(
            str(audio_file_path.resolve()),
            path_or_hf_repo=model,
            language="en",
            word_timestamps=True,
        )
        # make parent directories if they do not exist
        textfile_path.parent.mkdir(parents=True, exist_ok=True)
        jsonfile_path.parent.mkdir(parents=True, exist_ok=True)
        # write the transcription to a text file
        with open(textfile_path, "w", encoding="utf-8") as f:
            f.write(result["text"])
        # write the transcription to a json file
        with open(jsonfile_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info(f"Transcription successful! Text saved to {textfile_path} and JSON saved to {jsonfile_path}.")
    except Exception as e:
        logger.error(f"Error transcribing audio file {audio_file_path}: {e}")


if __name__ == "__main__":
    output = convert_audio_to_text("../../IwoJima_CombatRec_Josephy.wav")
    print(json.dumps(output, indent=2, ensure_ascii=False))