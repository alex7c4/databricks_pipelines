"""
Get raw Austin police department crime reports as JSONs.
https://data.austintexas.gov/Public-Safety/Crime-Reports/fdj4-gpfu/about_data
"""
import logging
import urllib

import requests

from src.lib.common_cfg import RAW_SAVE_PATH_DBFS


LOGGER = logging.getLogger(__name__)

# COMMAND ----------

LOCAL_SAVE_DIR = RAW_SAVE_PATH_DBFS / "austin_pd_crimes"

API_URL = "https://data.austintexas.gov/resource/fdj4-gpfu.json"
LIMIT = 50_000  # max limit, ~40mb per file

# COMMAND ----------

OFFSET = 0
counter = 0
while True:
    params = {"$limit": LIMIT, "$offset": OFFSET, "$order": "rep_date DESC"}
    params_str = urllib.parse.urlencode(params, safe="$")

    # get response
    response = requests.get(API_URL, params=params_str)
    response.raise_for_status()
    LOGGER.info(f"{counter:02d}) URL: {response.url}")

    # check if this is empty response --> no chunks left
    if response.text.strip() == "[]":
        LOGGER.info(f"Got empty response: '{response.text.strip()}'")
        break

    # save
    local_file_path = LOCAL_SAVE_DIR / f"austin_pd_crime_reports_{OFFSET}-{OFFSET+LIMIT}.json"
    local_file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(local_file_path, "wb") as fileo:
        fileo.write(response.content)

    OFFSET += LIMIT
    counter += 1

# COMMAND ----------

LOGGER.info("--DONE--")
