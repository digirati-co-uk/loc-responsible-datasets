import json
import logging
import collections

from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)


def flatten_dictionary_list(dictionary_list: list, key: str):
    flattened_list = [dictionary.get(key) for dictionary in dictionary_list]
    return flattened_list


def fetch_and_populate_subject_dataframe_from_source_data(
    source_directory: Path, output_path: Path
):
    data_for_df = collections.defaultdict(list)

    for json_file in source_directory.glob("**/subjects.json"):
        data = json.load(json_file.open("r", encoding="utf-8"))
        logger.info(f"Reading: {json_file}")

        data_for_df["congress"].append(data.get("request", {}).get("congress"))
        data_for_df["billNumber"].append(data.get("request", {}).get("billNumber"))
        data_for_df["billType"].append(data.get("request", {}).get("billType"))

        subjects = data.get("subjects", {})
        legislative_subjects = subjects.get("legislativeSubjects", [])
        legislative_subjects = flatten_dictionary_list(legislative_subjects, "name")
        policy_area = subjects.get("policyArea", {}).get("name", "")

        data_for_df["legislativeSubjects"].append(legislative_subjects)
        data_for_df["policyArea"].append(policy_area)

    df = pd.DataFrame.from_dict(data_for_df)
    df.to_csv(output_path, compression="gzip", index=False)
