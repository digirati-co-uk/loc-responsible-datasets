import json
import pandas as pd
import fsspec

from .location import (
    init_location,
)
from .api import (
    BILL_SUBFIELDS,
    TEXT_SUBFIELD,
)


def is_bill_processed(bill_status):
    bill_processed = [bill_status.get("bill", {}).get("processed")]
    subfields_processed = []
    for v in bill_status.get("subfields", {}).values():
        if v:
            subfields_processed.append(v.get("processed") and v.get("present"))
    bill_texts_processed = []
    if text_versions := bill_status.get("subfields", {}).get("textVersions", {}):
        for v in text_versions.get("bill_texts").values():
            bill_texts_processed.append(v.get("processed"))
    all_processed = bill_processed + subfields_processed + bill_texts_processed
    return all(all_processed)


def is_page_processed(page_status):
    is_processed = []
    for bill_path, bill_status in page_status.get("bills", {}).items():
        is_processed.append(is_bill_processed(bill_status))
    return all(is_processed)


def bill_overview_record(bill_path: str, bill_status: dict):
    congress, house, bill_number = bill_path.split("/")
    record = {
        "congress": congress,
        "house": house,
        "bill_number": bill_number,
        "processed": bill_status.get("bill", {}).get("processed", False),
    }
    for k in BILL_SUBFIELDS.keys():
        record[f"{k}_present"] = False
        record[f"{k}_processed"] = False
    record["bill_texts_present"] = 0
    record["bill_texts_processed"] = 0

    for k, v in bill_status.get("subfields", {}).items():
        if v:
            record[f"{k}_present"] = v.get("present", False)
            record[f"{k}_processed"] = v.get("processed", False)
        else:
            record[f"{k}_present"] = False
            record[f"{k}_processed"] = False
        if k == TEXT_SUBFIELD and v:
            for t in v.get("bill_texts", {}).values():
                record["bill_texts_present"] += 1
                if t.get("processed"):
                    record["bill_texts_processed"] += 1
    return record


def detailed_bill_record(
    source_filesystem: fsspec.filesystem,
    bill_path: str,
    bill_status: dict,
    bills_dir: str,
):
    congress, house, bill_number = bill_path.split("/")
    full_bill_path = f"{bills_dir}{bill_path}/"
    record = {
        "congress": congress,
        "house": house,
        "bill_number": bill_number,
        "bill": False,
        "text_formats": [],
    }
    for k in BILL_SUBFIELDS.keys():
        record[k] = False
    files = list(source_filesystem.glob(f"{full_bill_path}*"))
    json_files = filter(lambda x: x.endswith(".json"), files)
    other_files = filter(lambda x: not x.endswith(".json"), files)

    stored_file_suffixes = [f.split(bill_number)[-1] for f in other_files]
    file_subfields = {"bill": "bill", **BILL_SUBFIELDS}
    for f in json_files:
        for k, v in file_subfields.items():
            if f.endswith(f"{v}.json"):
                record[k] = True
    text_file_path = f"{full_bill_path}text.json"
    if source_filesystem.exists(text_file_path):
        text_formats = []
        text_json = json.load(source_filesystem.open(text_file_path, "r"))
        for version in text_json.get("textVersions"):
            text_type = version.get("type")
            for format in version.get("formats"):
                format_type = format.get("type")
                text_formats.append((text_type, format_type))
        record["text_formats"] = text_formats
    return record


def page_status_dataframe_by_congress(
    source_filesystem: fsspec.filesystem,
    source_dir: str,
    congress: int,
    output_dir: str,
):
    status_pages = source_filesystem.glob(f"{source_dir}{congress}*.status.json")
    bill_records = []
    for page in status_pages:
        status_data = json.load(source_filesystem.open(page, "r"))
        for bill_path, bill_status in status_data.get("bills", {}).items():
            bill_records.append(bill_overview_record(bill_path, bill_status))
    df = pd.DataFrame.from_records(bill_records)
    df.to_csv(
        f"{output_dir}{congress}_bill_status.csv.gz", compression="gzip", index=False
    )


def bill_status_dataframe_by_congress(
    source_filesystem: fsspec.filesystem,
    status_dir: str,
    bills_dir: str,
    congress: int,
    output_dir: str,
):
    status_pages = source_filesystem.glob(f"{status_dir}{congress}*.status.json")
    bill_records = []
    for page in status_pages:
        status_data = json.load(source_filesystem.open(page, "r"))
        for bill_path, bill_status in status_data.get("bills", {}).items():
            bill_records.append(
                detailed_bill_record(
                    source_filesystem=source_filesystem,
                    bill_path=bill_path,
                    bill_status=bill_status,
                    bills_dir=bills_dir,
                )
            )
    df = pd.DataFrame.from_records(bill_records)
    df.to_csv(
        f"{output_dir}{congress}_bill_status.csv.gz", compression="gzip", index=False
    )


def congress_page_status_dataframes(
    source_location: str,
    output_location: str,
):
    source_filesystem, source_dir = init_location(source_location, is_dir=True)
    output_filesystem, output_dir = init_location(
        output_location, is_dir=True, is_dest=True
    )
    status_pages = source_filesystem.glob(f"{source_dir}*.status.json")
    congresses = set([p.split("/")[-1].split("_")[0] for p in status_pages])

    for congress in congresses:
        print(f"Congress: {congress}")
        page_status_dataframe_by_congress(
            source_filesystem=source_filesystem,
            source_dir=source_dir,
            congress=congress,
            output_dir=output_dir,
        )


def congress_bill_status_dataframes(
    source_location: str,
    output_location: str,
):
    source_filesystem, source_dir = init_location(source_location, is_dir=True)
    output_filesystem, output_dir = init_location(
        output_location, is_dir=True, is_dest=True
    )
    status_source_dir = f"{source_dir}source_pages/"
    bills_source_dir = f"{source_dir}source_bills/"
    status_pages = source_filesystem.glob(f"{status_source_dir}*.status.json")
    congresses = set([p.split("/")[-1].split("_")[0] for p in status_pages])

    for congress in congresses:
        print(f"Congress: {congress}")
        bill_status_dataframe_by_congress(
            source_filesystem=source_filesystem,
            status_dir=status_source_dir,
            bills_dir=bills_source_dir,
            congress=congress,
            output_dir=output_dir,
        )
