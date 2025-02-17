import fsspec
from pathlib import Path


def init_location(
    location: str, is_dir: bool = False, is_dest: bool = False
) -> tuple[fsspec.filesystem, str]:
    if is_dir:
        location = location.rstrip("/") + "/"
    if location.startswith("s3://"):
        fs = fsspec.filesystem("s3")
    else:
        fs = fsspec.filesystem("file")
        if is_dest:
            _path = Path(location)
            if is_dir:
                _path.mkdir(parents=True, exist_ok=True)
            else:
                _path.parent.mkdir(parents=True, exist_ok=True)
    return fs, location
