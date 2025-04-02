import importlib.util

import logging

import re
import json
import pandas as pd
from collections import defaultdict
import xml.etree.ElementTree as ET

from pathlib import Path

logger = logging.getLogger(__name__)


def parse_marc_xml(file_path: Path):
    """
    Takes MARCXML file path and parses it into a dictionary/ JSON format with field, subfield keys
    """

    tree = ET.parse(file_path)
    root = tree.getroot()

    namespace = {"marc": "http://www.loc.gov/MARC21/slim"}
    records = []

    for record in root.findall("marc:record", namespace):
        record_dict = {}

        # Extract control fields
        for controlfield in record.findall("marc:controlfield", namespace):
            tag = controlfield.attrib["tag"]
            record_dict[tag] = controlfield.text

        # Extract data fields
        for datafield in record.findall("marc:datafield", namespace):
            tag = datafield.attrib["tag"]
            subfields = datafield.findall("marc:subfield", namespace)

            subfield_data = {sf.attrib["code"]: sf.text for sf in subfields}

            if tag in record_dict:
                if isinstance(record_dict[tag], list):
                    record_dict[tag].append(subfield_data)
                else:
                    record_dict[tag] = [record_dict[tag], subfield_data]
            else:
                record_dict[tag] = subfield_data

        records.append(record_dict)

    return records


# def load_variable_from_file(file_path, variable_name):
#     spec = importlib.util.spec_from_file_location("module_name", file_path)
#     module = importlib.util.module_from_spec(spec)
#     spec.loader.exec_module(module)
#     return getattr(module, variable_name, None)


def contains_japanese(text: str):
    """Check if a string contains Japanese characters (Hiragana, Katakana, or Kanji)."""
    if text is None:
        return False
    return bool(re.search(r"[\u3040-\u30FF\u4E00-\u9FFF]", text))


def filter_dict_by_key_value(data, key, value):
    res = [d for d in data if d.get(key) == value]
    if res:
        return res[0]
    else:
        res


def get_pointers(key):
    pointer, subpointer = key.split("/")[0].split("-")
    pointer = pointer.replace(" ", "")
    subpointer = subpointer.split("$")[0].replace(" ", "")
    return pointer, subpointer


def to_continue(filter_on, pointer, subpointer, to_exclude):
    if subpointer == "00":
        return True
    if pointer == "650":
        return True
    if pointer in to_exclude:
        return True
    if pointer.startswith("3") or pointer.startswith("5"):
        return True
    if filter_on:
        if pointer not in list(filter_on.keys()):
            return True
    return False


def get_transliteration_pairs(
    record: dict, filter_on: dict = {}, to_exclude: list = []
):
    pairs = defaultdict(list)
    lccn = record.get("010").get("a").strip()

    original_scripts = record.get("880")
    if isinstance(original_scripts, dict):
        original_scripts = [original_scripts]
    for script in original_scripts:
        pointer, subpointer = get_pointers(script.get("6"))

        if to_continue(filter_on, pointer, subpointer, to_exclude):
            continue

        if filter_on.get(pointer):
            script_subfields = [
                (key, value)
                for key, value in script.items()
                if contains_japanese(value) and key in filter_on[pointer]
            ]
        else:
            script_subfields = [
                (key, value)
                for key, value in script.items()
                if contains_japanese(value)
            ]

        transliterated_field = record.get(pointer)
        if isinstance(transliterated_field, list):
            transliterated_field = filter_dict_by_key_value(
                transliterated_field, "6", f"880-{subpointer}"
            )
        if not transliterated_field:
            continue
        transliterated_texts = [
            transliterated_field.get(subfield) for subfield, _ in script_subfields
        ]

        for i, (subfield, org_script) in enumerate(script_subfields):
            pairs["lccn"].append(lccn)
            pairs["field"].append(pointer)
            pairs["subfield"].append(subfield)
            pairs["original_script"].append(org_script)
            pairs["transliterated_text"].append(transliterated_texts[i])

    return pairs


# class Assembler(object):
#     def __init__(self, file_path: Path, filter_on: dict = {}, to_exclude: list = []):
#         self.parsed_xml = parse_marc_xml(file_path)
#         self.filter_on = filter_on
#         self.to_exclude = to_exclude

#     def jp_eng_string_df(self):

#         df_data = defaultdict(list)

#         for i, record in enumerate(self.parsed_xml):
#             try:
#                 transliterated_pairs = get_transliteration_pairs(
#                     record, self.filter_on, self.to_exclude
#                 )
#                 for key, values in transliterated_pairs.items():
#                     df_data[key].extend(values)
#             except Exception as e:
#                 logger.info(f"{i}: Error - {e}")

#         df = pd.DataFrame.from_dict(df_data)

#         return df.drop_duplicates()


def assemble_transliteration_df(
    file_path: Path, filter_on: dict = {}, to_exclude: list = []
):
    parsed_xml = parse_marc_xml(file_path)

    df_data = defaultdict(list)

    for i, record in enumerate(parsed_xml):
        try:
            transliterated_pairs = get_transliteration_pairs(
                record, filter_on, to_exclude
            )
            for key, values in transliterated_pairs.items():
                df_data[key].extend(values)
        except Exception as e:
            logger.info(f"{i}: Error - {e}")

    df = pd.DataFrame.from_dict(df_data)

    return df.drop_duplicates()
