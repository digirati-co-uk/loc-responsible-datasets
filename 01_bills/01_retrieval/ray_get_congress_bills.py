import os
import typer
import ray
import logging

from typing_extensions import Annotated

logger = logging.getLogger("ray")
logger.setLevel(logging.DEBUG)


@ray.remote(num_cpus=1)
def ray_wrapper(log_level: str, **kwargs):
    from utils.fetch_store import (
        fetch_and_store_congress_bills,
    )

    logger.debug(f"Running fetch_and_store_congress_bills")
    fetch_and_store_congress_bills(**kwargs)


def get_congress_bills(
    api_key: Annotated[
        str,
        typer.Argument(
            help="API key for the Congress.gov API instance",
            envvar="CONGRESS_GOV_API_KEY",
        ),
    ],
    api_url: Annotated[
        str, typer.Option(help="Base url for the Congress.gov API instance.")
    ] = "https://api.congress.gov/v3/",
    congress: Annotated[
        int, typer.Option(help="Congress to fetch and store bill pages for")
    ] = 111,
    source_location: Annotated[
        str,
        typer.Option(
            help="Location of JSON file containing the source page with list of bills. Must be a s3 uri."
        ),
    ] = "s3://loc-responsible-datasets-source-data/01_bills/source_pages",
    output_location: Annotated[
        str,
        typer.Option(
            help="Location to store the bill data fetched from the API. Must be an s3 uri."
        ),
    ] = "s3://loc-responsible-datasets-source-data/01_bills/source_bills",
    overwrite: Annotated[
        bool,
        typer.Option(help="Whether to refetch data and overwrite existing bill files"),
    ] = False,
    log_level: Annotated[
        str,
        typer.Option(
            help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
        ),
    ] = "INFO",
):
    ray.init()

    result = ray_wrapper.remote(
        api_url=api_url,
        api_key=api_key,
        congress=congress,
        source_location=source_location,
        output_location=output_location,
        overwrite=overwrite,
        log_level=log_level,
    )
    ray.get(result)


if __name__ == "__main__":
    typer.run(get_congress_bills)
