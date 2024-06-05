# Databricks notebook source
"""
Read and process raw austin police report JSON files to the bronze table.
"""
import os, sys  # isort: skip ; pylint: disable=multiple-imports
sys.path.append(os.environ.get("BUNDLE_SOURCE_PATH", "."))

# COMMAND ----------

import pyspark.sql.types as T

from src.lib.common_cfg import RAW_SAVE_PATH
from src.lib.spark import enable_optimized_write, get_spark


# COMMAND ----------

RESULT_TABLE = "bronze.austin_pd_codes"
RAW_FILES_PATH = RAW_SAVE_PATH / "austin_pd_codes" / "austin_police_codes.csv"

# COMMAND ----------

# Read raw files
spark = get_spark()

schema = T.StructType(
    [
        T.StructField("crime_type", T.StringType(), metadata={"comment": "Crime type"}),
        T.StructField(
            "nibrs_ucr",
            T.StringType(),
            metadata={"comment": "National Incident-Based Reporting System / Uniform Crime Reporting codes"}
        ),
        T.StructField("description", T.StringType(), metadata={"comment": "Description"}),
        T.StructField("apd_code", T.IntegerType(), metadata={"comment": "Austin Police Department code"}),
        T.StructField("ext", T.StringType(), metadata={"comment": "Extension code"}),
        T.StructField("offense", T.StringType(), metadata={"comment": "Offense description"}),
    ]
)

data_df = spark.read.csv(
    path=RAW_FILES_PATH.as_posix(),
    header=True,
    schema=schema,
    enforceSchema=False,
    mode="FAILFAST",
)

# COMMAND ----------

# Write
enable_optimized_write()

spark.sql("CREATE SCHEMA IF NOT EXISTS bronze")
# spark.sql(f"DROP TABLE IF EXISTS {RESULT_TABLE}")

(
    data_df
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", True)
    .saveAsTable(RESULT_TABLE)
)

spark.sql(f"OPTIMIZE {RESULT_TABLE} ZORDER BY (apd_code)")
spark.sql(f"VACUUM {RESULT_TABLE}")
