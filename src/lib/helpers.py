from pathlib import Path

import requests


def download_file(file_url: str, save_path: Path) -> Path:
    """Download a file and save it.

    :param file_url: File location
    :param save_path: Where to save the file
    :return: Path to the saved file
    """
    save_path.parent.mkdir(parents=True, exist_ok=True)

    with requests.get(file_url, stream=True) as r:
        r.raise_for_status()
        with save_path.open(mode="wb") as fileo:
            for chunk in r.iter_content(chunk_size=1024 * 1024 * 1):  # 1mb
                fileo.write(chunk)

    return save_path
