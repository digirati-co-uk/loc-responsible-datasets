"""
Annotate the transcribed text with entities and (optional) timestamps.
"""

import logging
from pathlib import Path
import json
import spacy
from spacy.tokens import Token, Doc
from spacy.training import iob_to_biluo

logger = logging.getLogger(__name__)


def flatten_json(json_data, norm_ws=False):
    """
    Flatten the JSON data to extract text and timestamps.

    Args:
        json_data (dict): The JSON data containing transcription details.

    Returns:
        list: A list of tuples containing text and its corresponding timestamps.
    """
    flattened = []
    for segment in json_data.get("segments", []):
        for word in segment.get("words", []):
            text = word.get("word", "").strip()
            start_time = word.get("start", 0)
            end_time = word.get("end", 0)
            if start_time > 0:
                start_time = start_time * 1000  # Convert to milliseconds
            if end_time > 0:
                end_time = end_time * 1000  # Convert to milliseconds
            flattened.append(dict(text=text, start_time=start_time, end_time=end_time))
    flattened_text = " ".join([item["text"] for item in flattened])
    if norm_ws:
        # replace multiple spaces with a single space
        flattened_text = " ".join(flattened_text.split())
    return flattened, flattened_text


def annotate_transcription(
    json_file: Path,
    output_file: Path,
    model: str = "en_core_web_trf",
):
    """
    Annotate the transcribed text with entities and (optional) timestamps.

    Args:
        output_file (Path): Path to save the annotated output.
        model (str): Spacy model to use for entity recognition.
    """
    try:
        nlp = spacy.load(model)
        with open(json_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        flattened, plaintext = flatten_json(json_data)
        # Set the extensions for start and end times on the Token class
        # This allows us to store custom attributes on tokens
        Token.set_extension("start_time", default=None, force=True)
        Token.set_extension("end_time", default=None, force=True)
        # Add the words to the Doc object
        doc = Doc(nlp.vocab, words=[item["text"] for item in flattened])
        # run the NLP pipeline on the doc
        doc = nlp(doc)
        # iterate the tokens and set the start and end times
        # as custom attributes of those tokens
        for i, token in enumerate(doc):
            token._.end_time = int(flattened[i]["end_time"])
            token._.start_time = int(flattened[i]["start_time"])
        # Convert the doc to a list of dictionaries with text and entity info
        annotated_data = []
        # Get the entities in BILOU format
        tags = iob_to_biluo(
            [
                token.ent_iob_
                + (
                    f"-{token.ent_type_}"
                    if (token.ent_type_ and token.ent_type_ != "O")
                    else ""
                )
                for token in doc
            ]
        )
        print(f"Length of doc: {len(doc)}")
        for i, token in enumerate(doc):
            if token.ent_iob_ != "O" and token.ent_type_ != "O":
                suffix = f"-{token.ent_type_}"
            else:
                suffix = ""
            entity_iob = token.ent_iob_ + suffix
            entity_bilou = tags[i]
            annotated_data.append(
                {
                    "text": token.text,
                    "start_time": getattr(token._, "start_time", None),
                    "end_time": getattr(token._, "end_time", None),
                    "iob": entity_iob,
                    "bilou": entity_bilou,
                }
            )
        # Write the annotated data to the output file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(annotated_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Error processing JSON file {json_file}: {e}")
        return


if __name__ == "__main__":
    # Example usage
    annotate_transcription(
        json_file="/Users/matt.mcgrattan/code/loc-responsible-datasets/local_data/04_speech_to_text/source_txt/childrens_express/Santora/Santora.json",
        output_file="/Users/matt.mcgrattan/code/loc-responsible-datasets/local_data/04_speech_to_text/source_txt/childrens_express/Santora/Santora_annotated.json",
    )
