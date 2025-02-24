import typer
import logging
import functools

from config import ARGUMENTS
from typing_extensions import Annotated
from pathlib import Path
from utils.resampler import Resampler

import pandas as pd

RESAMPLING_TYPE = {"random_undersampling": functools}


def apply_sampling(
    source_df_path: Annotated[
        Path, typer.Option(help="Location to load in original dataset from.")
    ] = Path(
        "../../local_data/01_bills/generated_data/concat_compiled_subjects_with_text.csv.gz"
    ),
    output_directory: Annotated[
        Path, typer.Option(help="Location to store the resampling dataset.")
    ] = Path("../../local_data/01_bills/generated_data/resampled_data"),
    resampling_type1: Annotated[
        str,
        typer.Option(
            help="First resampling technique to be applied to original dataset (random_undersampling, random_oversampling, knn_undersampling, near_miss_undersampling)"
        ),
    ] = "random_undersampling",
    resampling_type2: Annotated[
        str,
        typer.Option(
            help="Second resampling technique to be applied to original dataset (random_undersampling, random_oversampling, knn_undersampling, near_miss_undersampling)"
        ),
    ] = "random_oversampling",
    arguments: Annotated[
        str,
        typer.Option(help="Key to access correct ARGUMENTS in config.py"),
    ] = "rus_ros",
    attribute_to_balance: Annotated[
        str,
        typer.Option(help="Attribute that the dataset will be balanced on"),
    ] = "legislativeSubjects",
    random_state: Annotated[
        int,
        typer.Option(
            help="Random state used when applying resampling techniques for repeatability"
        ),
    ] = 42,
    log_level: Annotated[
        str,
        typer.Option(
            help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
        ),
    ] = "INFO",
):
    """
    Local CLI Wrapper for the Resampling object.
    """

    log_level = log_level.upper()
    level_enum = getattr(logging, log_level, None)
    if not isinstance(level_enum, int):
        raise typer.BadParameter(f"Invalid log level: {log_level}")
    logging.basicConfig(
        level=level_enum,
        format="%(asctime)s - %(name)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s",
    )

    dataset = pd.read_csv(
        source_df_path, compression="gzip", converters={"legislativeSubjects": pd.eval}
    )
    for i, resampling_type in enumerate([resampling_type1, resampling_type2]):
        resampler = Resampler(dataset=dataset, random_state=random_state)
        resampling_method = getattr(resampler, resampling_type)
        resampled_data = resampling_method(
            attribute_to_balance=attribute_to_balance, **ARGUMENTS.get(arguments)[i]
        )
        dataset = resampled_data

    output_path = output_directory / f"{attribute_to_balance}_{arguments}.csv.gz"
    print(f"Saving to: {output_path=} ...")
    resampled_data.to_csv(output_path, compression="gzip", index=False)


if __name__ == "__main__":
    typer.run(apply_sampling)
