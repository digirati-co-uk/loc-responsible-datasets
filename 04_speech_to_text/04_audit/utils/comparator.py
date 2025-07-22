"""
Compare two CSV files containing the original machine generated data and the entity data.
"""

import logging
from glob import glob

import matplotlib.pyplot as plt
import pandas
import pandas as pd
import seaborn as sns
from jiwer import wer, cer

logger = logging.getLogger(__name__)


def comparse_csv_files_simple(original_file: str, review_file: str):
    """
    Compare two CSV files containing the original machine generated data and the entity data.

    :param original_file: Path to the original CSV file.
    :param review_file: Path to the entity CSV file.
    :return: DataFrame containing the comparison results.
    """
    print(f"Comparing {original_file} with {review_file}")
    original_df = pd.read_csv(original_file)
    review_df = pd.read_csv(review_file)
    original_text = original_df["text"].astype(str).tolist()
    review_text = review_df["text"].astype(str).tolist()
    if len(original_text) == len(review_text):
        wer_value = wer(" ".join(original_text), " ".join(review_text))
        cer_value = cer(" ".join(original_text), " ".join(review_text))
        # count the number of rows in review_df where the text_fail column is not NaN or null

        text_fail_count = review_df["text_fail"].notna().sum()
        text_fail_percentage = text_fail_count / len(review_text)
        entity_fail_count = review_df["entity_type_fail"].notna().sum()
        # rows with entities that are not NaN or null
        original_entity_count = original_df["entity_type"].notna().sum()
        entity_fail_percentage = (
            entity_fail_count / original_entity_count
            if original_entity_count > 0
            else 0
        )
        # count the number of rows where there is a PERSON entity in the review_df
        # but not in the original_df
        missing_person_entities = int(
            (
                (review_df["entity_type"] == "PERSON")
                & (original_df["entity_type"] != "PERSON")
            ).sum()
        )
        extra_person_entities = (
            (review_df["entity_type"] != "PERSON")
            & (original_df["entity_type"] == "PERSON")
        ).sum()
        total_review_person_entities = int((review_df["entity_type"] == "PERSON").sum())

        # Note that the number of text fails is not the same as the number of text errors,
        # because sometimes reviews have made some small corrections without flagging
        # it as a failure.
        return (
            len(original_text),
            wer_value,
            cer_value,
            text_fail_count,
            text_fail_percentage,
            original_entity_count,
            entity_fail_count,
            entity_fail_percentage,
            missing_person_entities,
            extra_person_entities,
            total_review_person_entities,
        )
    else:
        return None, None, None, None, None, None, None, None, None, None, None


def collate_stats(input_directory, review_directory):
    """
    Collate statistics from multiple CSV files in the input directory and review directory.
    :param input_directory: Path to the directory containing original CSV files.
    :param review_directory: Path to the directory containing review CSV files.
    :return: DataFrame containing collated statistics.
    """
    import os

    stats = pandas.DataFrame()
    for filename in glob(
        os.path.join(input_directory, "**/*_annotated.csv"), recursive=True
    ):
        review_file = None
        # replace input_directory with review_directory in the filename
        candidate_review_file = filename.replace(input_directory, review_directory)
        # the filename is probably not the same, so check if any CSV file exists in the review directory
        try:
            digit = [x for x in os.path.basename(filename) if x.isdigit()][0]
        except IndexError:
            digit = None
        for review_candidate in glob(
            os.path.join(os.path.dirname(candidate_review_file), "**/*.csv"),
            recursive=True,
        ):
            try:
                review_digit = [
                    x for x in os.path.basename(review_candidate) if x.isdigit()
                ][0]
            except IndexError:
                review_digit = None
            if review_digit == digit:
                # we have a match, so compare the files
                review_file = review_candidate
                break
        if review_file:
            (
                text_length,
                csv_wer,
                csv_cer,
                text_fail,
                text_fail_percentage,
                original_ent_count,
                entity_fail_count,
                entity_fail_percentage,
                missing_person_count,
                extra_person_count,
                total_review_person_count,
            ) = comparse_csv_files_simple(
                original_file=filename,
                review_file=review_file,
            )
            # Append the statistics to the stats DataFrame
            if text_length is not None:
                stats = pandas.concat(
                    [
                        stats,
                        pandas.DataFrame(
                            [
                                {
                                    "filename": os.path.basename(filename),
                                    "text_length": text_length,
                                    "wer": csv_wer,
                                    "cer": csv_cer,
                                    "text_fail": text_fail,
                                    "text_fail_percentage": text_fail_percentage,
                                    "original_entity_count": original_ent_count,
                                    "entity_fail_count": entity_fail_count,
                                    "entity_fail_percentage": entity_fail_percentage,
                                    "missing_person_count": missing_person_count,
                                    "extra_person_count": extra_person_count,
                                    "total_review_person_count": total_review_person_count,
                                }
                            ]
                        ),
                    ],
                    ignore_index=True,
                )
    # add the word error count to each row
    stats["word_error_count"] = stats["wer"] * stats["text_length"]
    # word error count micro-averaged across all files
    stats["micro_averaged_word_error_count"] = (
        stats["word_error_count"].sum() / stats["text_length"].sum()
    )
    # calculate the mean WER and CER
    stats["mean_wer"] = stats["wer"].mean()
    stats["mean_cer"] = stats["cer"].mean()
    stats["mean_text_fail"] = stats["text_fail"].mean()
    # calculate the total number of files
    stats["total_files"] = len(stats)
    # calculate the total number of text failures
    stats["total_text_fail"] = stats["text_fail"].sum()
    # calculate the text fail percentage for each row
    stats["text_fail_percentage"] = (stats["text_fail"] / stats["text_length"]).fillna(
        0
    ) * 100  # avoid division by zero
    # calculate the total number of text failures
    stats["total_text_fail"] = stats["text_fail"].sum()
    # calculate the total text length
    stats["total_text_length"] = stats["text_length"].sum()
    # # calculate the text fail percentage as a percentage of the total text length across all files
    stats["total_text_fail_percentage"] = (
        stats["total_text_fail"] / stats["total_text_length"]
    ) * 100
    stats["total_entity_fail_count"] = stats["entity_fail_count"].sum()
    stats["total_original_entity_count"] = stats["original_entity_count"].sum()
    stats["total_entity_fail_percentage"] = (
        (stats["total_entity_fail_count"] / stats["total_original_entity_count"]) * 100
        if stats["total_original_entity_count"].sum() > 0
        else 0
    )
    stats["mean_original_entity_count"] = stats["original_entity_count"].mean()
    stats["mean_missing_person_count"] = stats["missing_person_count"].mean()
    stats["mean_extra_person_count"] = stats["extra_person_count"].mean()
    stats["mean_total_review_person_count"] = stats["total_review_person_count"].mean()
    # calculate the sum of people in the review files
    total_review_persons = stats["total_review_person_count"].sum()
    # calculate the sum of missing persons
    total_missing_persons = stats["missing_person_count"].sum()
    # add these to the stats DataFrame
    stats["total_review_persons"] = total_review_persons
    stats["total_missing_persons"] = total_missing_persons
    # save the stats DataFrame to a CSV file
    output_file = os.path.join(input_directory, "collated_stats.csv")
    stats.to_csv(output_file, index=False, encoding="utf-8")
    # generate a histogram of the text_fail column

    plt.figure(figsize=(10, 6))
    sns.histplot(stats["text_fail"], bins=50, edgecolor="black")
    plt.title("Distribution of Incorrect Words (review)")
    plt.xlabel("Number of incorrect words (per file)")
    plt.ylabel("Number of Files")
    plt.xlim(0, stats["text_fail"].max() + 10)
    # save the plot to a JPEG file
    plt.savefig(
        os.path.join(input_directory, "text_fail_histogram.jpg"),
        dpi=300,
        bbox_inches="tight",
    )
    # Generate a histogram of the entity_fail_count column stacked on top of original_entity_count
    # with different colors for entity_fail_count and original_entity_count
    plt.figure(figsize=(10, 6))
    sns.histplot(stats["entity_fail_count"], bins=50, edgecolor="black")

    plt.title("Distribution of Entity Failures (review)")
    plt.xlabel("Number of entity failures (per file)")
    plt.ylabel("Number of Files")
    plt.xlim(0, stats["entity_fail_count"].max() + 10)
    # save the plot to a JPEG file
    plt.savefig(
        os.path.join(input_directory, "entity_fail_histogram.jpg"),
        dpi=300,
        bbox_inches="tight",
    )
    # Generate a histogram of the missing_person_count column
    plt.figure(figsize=(10, 6))
    sns.histplot(stats["missing_person_count"], bins=50, edgecolor="black")

    plt.title("Distribution of missing PERSONs (review)")
    plt.xlabel("Number of missing PERSONs (per file)")
    plt.ylabel("Number of Files")
    # save the plot to a JPEG file
    plt.savefig(
        os.path.join(input_directory, "missing_person_histogram.jpg"),
        dpi=300,
        bbox_inches="tight",
    )


if __name__ == "__main__":
    collate_stats(
        input_directory="../../../local_data/04_speech_to_text/output/minnesota_starvation_transcripts",
        review_directory="../../../local_data/04_speech_to_text/LOC_Review_Files_For_Digirati/minnesota_starvation_transcripts",
    )
    collate_stats(
        input_directory="../../../local_data/04_speech_to_text/output/",
        review_directory="../../../local_data/04_speech_to_text/LOC_Review_Files_For_Digirati/",
    )
    collate_stats(
        input_directory="../../../local_data/04_speech_to_text/output/childrens_express",
        review_directory="../../../local_data/04_speech_to_text/LOC_Review_Files_For_Digirati/childrens_express",
    )
