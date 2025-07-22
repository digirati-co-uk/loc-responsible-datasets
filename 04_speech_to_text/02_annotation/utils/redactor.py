import json
import spacy
from fastcoref import spacy_component, LingMessCoref
from annotate import flatten_json
from spacy.tokens import Token, Doc, Span
import logging
import pandas as pd
from collections import defaultdict
import faker
import random

logger = logging.getLogger(__name__)


def coreference_parsing(json_file, model="en_core_web_trf", grouped=("PERSON",)) -> Doc:
    """
    Parse coreferences in a JSON file preparatory to redaction
    with synthetic data generation.

    Returns a spaCy Doc object with coreference resolution groups assigned to tokens and spans which are
    entity types slected for grouping (defaults to PERSON entities).

    N.B. Current testing shows some potential issues with the coreference resolution model
    altering the entities identified by the ner pipeline. Further testing is required

    :param json_file: Path to the input JSON file.
    """
    with open(json_file, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    flattened, plaintext = flatten_json(json_data, norm_ws=True)
    nlp = spacy.load(model)
    # Load the coreference resolution model into a different pipeline
    coref = spacy.load(model, exclude=["parser", "lemmatizer", "ner", "textcat"])
    coref.add_pipe(
        "fastcoref",
    )
    # Set the extensions for start and end times on the Token class
    # This allows us to store custom attributes on tokens
    Token.set_extension("start_time", default=None, force=True)
    Token.set_extension("end_time", default=None, force=True)
    # Set the extension for coreference group on the Token class
    Token.set_extension("coref_group", default=None, force=True)
    Span.set_extension("coref_group", default=None, force=True)
    # Add the words to the Doc object
    source_doc = Doc(nlp.vocab, words=[item["text"] for item in flattened])
    # run the NLP pipeline on the doc
    doc = nlp(source_doc)
    coref_doc = coref(source_doc)
    # iterate the tokens and set the start and end times
    # as custom attributes of those tokens
    for i, token in enumerate(doc):
        token._.end_time = int(flattened[i]["end_time"])
        token._.start_time = int(flattened[i]["start_time"])
    # parse the coreference resolution clusters
    for i, cluster in enumerate(coref_doc._.coref_clusters):
        for term in cluster:
            for token in doc:
                if term[0] <= token.idx <= term[1]:  # Inclusive range
                    if token.ent_iob_ != "O" and token.ent_type_ in grouped:
                        # Only assign coreference group for PERSON entities
                        token._.coref_group = i  # Assign the coreference group index
    for ent in doc.ents:
        if ent.label_ in grouped:
            for token in ent:
                if token._.coref_group is not None:
                    ent._.coref_group = token._.coref_group
                    break
    return doc


def coreference_from_df(df, grouped=("PERSON",)):
    """
    Add coreference resolution groups to a DataFrame containing annotated text data.

    The purpose is to identify when entities of a certain type (e.g., PERSON) refer to the same entity
    in the text, and assign a coreference group index to those entities.

    For example, if two mentions of "John Doe" are found in the text, then both mentions will be assigned
     the same coreference group index. In some cases, the coreference group may pick out
     different forms of the same entity, such as "John Doe" and "Mr. Doe", although this is not guaranteed.

    :param df: Pandas DataFrame containing annotated text data.
    :param grouped: Tuple of entity types to consider for coreference resolution.
                    Default is ("PERSON",) to focus on person entities.
    """
    text = df["text"].tolist()
    model = LingMessCoref(device="cpu")  # Load the coreference resolution model
    preds = model.predict(
        [text], is_split_into_words=True
    )  # Predict coreferences for the text
    for idx, cluster_group in enumerate(preds[0].get_clusters(as_strings=False)):
        for cluster in cluster_group:
            start = cluster[0]
            end = cluster[1]
            indexed_range = range(start, end)
            for index in indexed_range:
                if df.iloc[index]["iob"].split("-")[-1] in grouped:
                    # add the coreference group to the DataFrame
                    df.at[index, "coref_group"] = int(idx)
    return df


def coreference_from_json(json_file, annotated_types=("PERSON",)):
    """
    Add coreference resolution groups to a JSON file containing annotated text data.

    The purpose is to identify when entities of a certain type (e.g., PERSON) refer to the same entity
    in the text, and assign a coreference group index to those entities.

    For example, if two mentions of "John Doe" are found in the text, then both mentions will be assigned
     the same coreference group index. In some cases, the coreference group may pick out
     different forms of the same entity, such as "John Doe" and "Mr. Doe", although this is not guaranteed.

    :param json_file: Path to the input JSON file containing annotated text data.
    :param annotated_types: Tuple of entity types to consider for coreference resolution.
                            Default is ("PERSON",) to focus on person entities.

    """
    df = pd.read_json(json_file)
    # Ensure the DataFrame has the necessary columns
    if "text" not in df.columns or "iob" not in df.columns:
        raise ValueError("DataFrame must contain 'text' and 'iob' columns.")
    df = coreference_from_df(df, annotated_types)
    # Save the DataFrame with coreference groups to a new JSON file
    output_file = json_file.replace("_annotated.json", "_annotated_coreference.json")
    df.to_json(output_file, orient="records", lines=False, force_ascii=False, indent=2)
    return df


def redact_simple(
    df,
    redacted_types=("PERSON", "ORGANIZATION"),
    redaction_text="REDACTED",
    redaction_type="text",
    wrapper="[]",
):
    """
    Redact entities in a DataFrame based on their coreference groups.

    :param df: Pandas DataFrame containing annotated text data with coreference groups.
    :param redacted_types: Tuple of entity types to redact. Defaults to ("PERSON", "ORGANIZATION").
    :param redaction_text: Text to replace the redacted entities with. Defaults to "REDACTED".
    :param redaction_type: Type of redaction to perform. Defaults to "text", which replaces the text of the entities.
                           If set to "type", it will replace the text with the entity type.
    :param wrapper: Tuple of strings to wrap the redaction text. Defaults to "[]".
    :return: DataFrame with redacted entities.
    """
    if redaction_type == "text":
        if wrapper:
            redaction_string = f"{wrapper[0]}{redaction_text}{wrapper[1]}"
        else:
            redaction_string = redaction_text
        for index, row in df.iterrows():
            if row["iob"].split("-")[-1] in redacted_types:
                df.at[index, "text"] = redaction_string
    elif redaction_type == "type":
        for index, row in df.iterrows():
            if row["iob"].split("-")[-1] in redacted_types:
                if wrapper:
                    df.at[index, "text"] = (
                        f"{wrapper[0]}{row['iob'].split('-')[-1]}{wrapper[1]}"
                    )
                else:
                    df.at[index, "text"] = row["iob"].split("-")[-1]
    return df


def redact_synthetic(df):
    """
    Redact entities in a DataFrame based on their coreference groups using synthetic data generation.

    Note, the assumption is that the DataFrame has already been processed to include coreference groups
    and that only PERSON entities are being redacted.

    :param df: Pandas DataFrame containing annotated text data with coreference groups.
    :return: DataFrame with redacted entities.
    """
    redaction_list = []
    # Identify PERSON entities. Note, that the entities
    # may span multiple tokens, so we need to group them by IOB tags, i.e. B-PERSON and I-PERSON.
    # constitute a single entity.
    entities_start = df[(df["iob"].str.startswith("B-PERSON"))].copy()
    entities_start["orig_index"] = entities_start.index
    # 2. Iterate over the entities and identify the start and end indices of each entity.
    for index, row in entities_start.iterrows():
        start_index = index
        end_index = index
        # Check if the next tokens are part of the same entity
        while end_index + 1 < len(df) and df.at[end_index + 1, "iob"].startswith(
            "I-PERSON"
        ):
            end_index += 1
        # Now we have the start and end indices of the entity
        # Calculate how long the entity is, i.e. is it a single token or multiple tokens
        entity_length = end_index - start_index + 1
        # loop over the tokens in the entity and construct the text
        entity_text = " ".join(df.loc[start_index:end_index, "text"].tolist())
        # We can replace the text with a synthetic name of the appropriate length
        # Note, that this is a placeholder and should be replaced with a proper
        # synthetic name generation logic
        coreference_group = row["coref_group"] if "coref_group" in row else None
        redaction_list.append(
            (start_index, end_index, entity_length, entity_text, coreference_group)
        )
    # identify the largest number in the coreference groups
    max_coref_group = df["coref_group"].max() if "coref_group" in df else -1
    grouped = defaultdict(list)
    for (
        start_index,
        end_index,
        entity_length,
        entity_text,
        coref_group,
    ) in redaction_list:
        if coref_group is not None and not pd.isna(coref_group):
            grouped[coref_group].append(
                (start_index, end_index, entity_length, entity_text)
            )
        else:
            # If there is no coreference group, we can assign a new one
            max_coref_group += 1
            grouped[max_coref_group].append(
                (start_index, end_index, entity_length, entity_text)
            )
    # Now we can iterate over the grouped entities and redact them
    # sort by group key
    grouped = dict(sorted(grouped.items(), key=lambda item: item[0]))
    # iterate the groups
    for group, entities in grouped.items():
        # gender = a random choice between male and female
        gender = random.choice(["M", "F"])
        max_length = max([entity[2] for entity in entities])
        # extract the longest original name in the group and store it for later
        # e.g. if the longest name is 3 tokens long, then
        longest_entity = max(entities, key=lambda x: x[2])
        original_name = longest_entity[3].split(" ")
        # our synthetic name will be of the same length
        # Assumption: last name is always present, this may not be true in all cases
        fake = faker.Faker()
        fake_name = []
        if gender == "M":
            for i in range(max_length - 1):
                fake_name.append(fake.first_name_male())
            fake_name.append(fake.last_name_male())
        elif gender == "F":
            fake_name = []
            for i in range(max_length - 1):
                fake_name.append(fake.first_name_female())
            fake_name.append(fake.last_name_female())
        logger.info(f"Replacing {' '.join(original_name)} with {' '.join(fake_name)}")
        for entity in entities:
            start_index, end_index, entity_length, entity_text = entity
            name_parts = None
            try:
            # find the position of entity_text in original_name
                name_indices = [original_name.index(n) for n in entity_text.split(" ")]
                # synthetic name parts will be replaced in the same order
                name_parts = [fake_name[i] for i in name_indices]
            except ValueError as e:
                logger.error(
                    f"Error finding entity text '{entity_text}' in original name '{original_name}': {e}"
                )

            # Replace each token in the entity span with the corresponding part of the synthetic name
            for i, idx in enumerate(range(start_index, end_index + 1)):
                if name_parts:
                    logger.debug("Original", original_name)
                    logger.debug("Fake", fake_name)
                    logger.debug("Text", entity_text)
                    logger.debug("Parts", name_parts)
                    logger.debug("Name_index", i)
                    logger.debug("Token_index", idx)
                    df.at[idx, "text"] = name_parts[i]
            logger.debug("==============")
            # assign the coreference group to the tokens
            for i in range(start_index, end_index + 1):
                df.at[i, "coref_group"] = group
    return df


if __name__ == "__main__":
    # coreference_parsing(
    #     json_file="../../../local_data/04_speech_to_text/source_txt/childrens_express/Two_Young_Delegates/2 KANSAS DELEGATES.json",
    #     model="en_core_web_trf",
    # )
    test = coreference_from_json(
        json_file="../../../local_data/04_speech_to_text/source_txt/childrens_express/Two_Young_Delegates/2 KANSAS DELEGATES_annotated.json"
    )
    new = redact_synthetic(test)
    new.to_json(
        "../../../local_data/04_speech_to_text/source_txt/childrens_express/Two_Young_Delegates/2 KANSAS DELEGATES_annotated_redacted.json",
        orient="records",
        lines=False,
        force_ascii=False,
        indent=2,
    )
