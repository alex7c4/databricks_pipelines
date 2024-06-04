# Databricks notebook source
import os, sys  # isort: skip
sys.path.append(os.environ.get("BUNDLE_SOURCE_PATH", "."))

# COMMAND ----------

"""Get raw Austin police department codes."""
import logging

from src.lib.common_cfg import RAW_SAVE_PATH_DBFS
from src.lib.helpers import download_file


LOGGER = logging.getLogger(__name__)

# COMMAND ----------

CODES_CSV_URL = "https://raw.githubusercontent.com/alex7c4/databricks_pipelines/main/raw_data/austin_police_codes.csv"
LOCAL_SAVE_DIR = RAW_SAVE_PATH_DBFS / "austin_pd_codes"

# COMMAND ----------

local_f_path = download_file(file_url=CODES_CSV_URL, save_path=LOCAL_SAVE_DIR / "austin_police_codes.csv")

# COMMAND ----------

LOGGER.info(f"File downloaded: {local_f_path}")
