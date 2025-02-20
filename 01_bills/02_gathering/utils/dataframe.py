import json
import logging
import collections

from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)


def format_dataframe(dataframe: pd.DataFrame):
    dataframe = dataframe.dropna(how="any", axis=0)
    for col in list(dataframe.columns):
        if isinstance(dataframe.iloc[0][col], float):
            dataframe[col] = dataframe[col].astype(int)

    return dataframe


def concat_dataframes(source_directory: Path, dataframe_file: str):
    dataframes = []
    for df_file in source_directory.glob(f"**/{dataframe_file}"):
        logger.info(f"Processing: {df_file}")
        try:
            df = pd.read_csv(df_file, compression="gzip")
            formatted_df = format_dataframe(df)
            dataframes.append(formatted_df)
        except Exception as e:
            print(e)

    full_dataframe = pd.concat(dataframes)

    full_dataframe_path = source_directory / f"concat_{dataframe_file}"
    full_dataframe.to_csv(full_dataframe_path, compression="gzip", index=False)
    return full_dataframe


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
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, compression="gzip", index=False)


def read_subjects(subjects_path: Path):
    data = json.load(subjects_path.open("r", encoding="utf-8"))

    subjects = data.get("subjects", {})
    legislativeSubjects = subjects.get("legislativeSubjects", [])
    legislativeSubjects = flatten_dictionary_list(legislativeSubjects, "name")
    policyArea = subjects.get("policyArea", {}).get("name", "")

    return legislativeSubjects, policyArea


def read_summaries(summaries_path: Path):
    data = json.load(summaries_path.open("r", encoding="utf-8"))
    ### DECIDE HOW TO READ THIS
    return


def read_bill_html_by_date(text_path: Path) -> str:
    data = json.load(text_path.open("r", encoding="utf-8"))
    textVersions = data.get("textVersions", [{}])
    filtered_textVersions = list(filter(lambda x: x.get("date"), textVersions))
    sorted_textVersions = sorted(filtered_textVersions, key=lambda d: d.get("date"))

    bill_html = ""
    bill_html_url = ""
    if sorted_textVersions:
        for version in sorted_textVersions[-1]["formats"]:
            if version.get("type") == "Formatted Text":
                bill_html_url = version.get("url")
                break

    if bill_html_url:
        bill_html_path = text_path.parent / f"{bill_html_url.split('/')[-1]}"
        if bill_html_path.exists():
            bill_html = bill_html_path.read_text(encoding="utf-8")
    return bill_html


# def read_bill_html_by_type(text_path: Path):
#     data = json.load(text_path.open("r", encoding="utf-8"))
#     textVersions = data.get("textVersions", [{}])

#     for version in textVersions:
#         if "Introduced in" in version.get("type"):
#             for format_ in version.get("formats"):
#                 if format_.get("type") == "Formatted Text":
#                     bill_html_url = format_.get("url")
#                     break

#     bill_html_path = text_path.parent / f"{bill_html_url.split('/')[-1]}"
#     bill_html = bill_html_path.read_text(encoding="utf-8")
#     return bill_html


def get_record(bill_dir: Path) -> dict:
    logger.info(f"Reading: {bill_dir}")

    bill_record = {}

    congress = bill_dir.parent.parent.name
    billType = bill_dir.parent.name
    billNumber = bill_dir.name

    subjects_path = bill_dir / "subjects.json"
    text_path = bill_dir / "text.json"

    billText = ""
    if text_path.exists() and subjects_path.exists():
        legislativeSubjects, policyArea = read_subjects(subjects_path)
        billText = read_bill_html_by_date(text_path)

    if billText:
        bill_record = {
            "congress": congress,
            "billType": billType,
            "billNumber": billNumber,
            "legislativeSubjects": legislativeSubjects,
            "policyArea": policyArea,
            "billText": billText,
        }

    return bill_record


def fetch_and_populate_subject_bill_text_dataframe_from_source_data(
    source_directory: Path, output_path: Path, glob_pattern: str
):
    data_for_df = []

    for bill_dir in source_directory.glob(glob_pattern):
        if not bill_dir.is_dir():
            continue

        if bill_record := get_record(bill_dir):
            data_for_df.append(bill_record)
        # try:
        #     bill_record = get_record(bill_dir)
        #     if bill_record:
        #         data_for_df.append(bill_record)
        #     else:
        #         logger.info("Issue")
        # except Exception as e:
        #     logger.info(e)

    df = pd.DataFrame(data_for_df)
    df.to_csv(output_path, compression="gzip", index=False)
