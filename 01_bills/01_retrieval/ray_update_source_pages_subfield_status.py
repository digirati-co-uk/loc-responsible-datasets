import os
import typer
import ray
import logging

from typing_extensions import Annotated

logger = logging.getLogger("ray")
logger.setLevel(logging.DEBUG)


@ray.remote
def ray_wrapper(log_level: str, **kwargs):
    from utils.fetch_store import (
        update_source_pages_subfield_processed_status,
    )

    logger.debug(f"Running update_source_pages_subfield_processed_status")
    update_source_pages_subfield_processed_status(**kwargs)


def ray_update_source_pages_subfield_status(
    source_location: Annotated[
        str,
        typer.Option(
            help="Location of JSON file containing the source page with list of bills. Must be a s3 uri."
        ),
    ] = "s3://loc-responsible-datasets-source-data/01_bills/source_pages",
    congress: Annotated[
        int, typer.Option(help="Congress to fetch and store bill pages for")
    ] = 111,
    subfield: Annotated[
        str, typer.Option(help="Congress to fetch and store bill pages for")
    ] = "textVersions",
    subfield_status: Annotated[
        bool, typer.Option(help="Congress to fetch and store bill pages for")
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
        source_location=source_location,
        congress=congress,
        subfield=subfield,
        subfield_status=subfield_status,
        log_level=log_level,
    )
    ray.get(result)


if __name__ == "__main__":
    typer.run(ray_update_source_pages_subfield_status)
