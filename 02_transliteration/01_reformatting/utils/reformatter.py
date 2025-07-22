import xml.etree.ElementTree as ET
from lxml import etree

import json

from pathlib import Path

import logging

logger = logging.getLogger(__name__)


def convert_txt_to_xml(txt_input_path: Path, xml_output_path: Path):
    marcxml_content = txt_input_path.read_text(encoding="utf-8")
    xml_output_path.write_text(marcxml_content, encoding="utf-8")

    logger.info(
        f"Conversion successful! The MARCXML file is saved as {xml_output_path}."
    )


def parse_marc_xml(file_path):
    logger.info(f"Parsing {file_path}...")
    tree = ET.parse(file_path)
    root = tree.getroot()

    namespace = {"marc": "http://www.loc.gov/MARC21/slim"}
    records = []

    for record in root.findall("marc:record", namespace):
        record_dict = {}

        for controlfield in record.findall("marc:controlfield", namespace):
            tag = controlfield.attrib["tag"]
            record_dict[tag] = controlfield.text

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


def convert_list_to_marcxml(marc_list: list, output_file: Path, make_unique=True):

    if make_unique:
        unique_data = list({json.dumps(d, sort_keys=True) for d in marc_list})
        marc_list = [json.loads(d) for d in unique_data]

    logger.info(f"MARC LIST LEN: {len(marc_list)}")

    collection = etree.Element("collection", xmlns="http://www.loc.gov/MARC21/slim")

    for record_dict in marc_list:
        record = etree.Element("record")

        for tag, value in record_dict.items():
            if isinstance(value, str):
                controlfield = etree.Element("controlfield", tag=tag)
                controlfield.text = value
                record.append(controlfield)

            elif isinstance(value, dict):
                datafield = etree.Element("datafield", tag=tag, ind1=" ", ind2=" ")
                for code, sub_value in value.items():
                    subfield = etree.Element("subfield", code=code)
                    subfield.text = sub_value
                    datafield.append(subfield)
                record.append(datafield)

            elif isinstance(value, list):
                for subfield_dict in value:
                    datafield = etree.Element("datafield", tag=tag, ind1=" ", ind2=" ")
                    for code, sub_value in subfield_dict.items():
                        subfield = etree.Element("subfield", code=code)
                        subfield.text = sub_value
                        datafield.append(subfield)
                    record.append(datafield)

        collection.append(record)
    print(len(collection))
    collection_tree = etree.ElementTree(collection)
    with output_file.open("wb") as f:
        collection_tree.write(
            f, pretty_print=True, xml_declaration=True, encoding="UTF-8"
        )

    logger.info(f"Converted MARCXML saved to {output_file}")
