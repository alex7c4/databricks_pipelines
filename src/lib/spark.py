"""Module with Spark related helpers"""

import pyspark.sql.functions as F
from pyspark.sql import Column, SparkSession


def get_spark() -> SparkSession:
    """Return SparkSession"""
    return SparkSession.builder.getOrCreate()


def comment(col_name: str, info: str) -> Column:
    """Add commend to Column. Will be visible during DESCRIBE table"""
    return F.col(col_name).alias(col_name, metadata={"comment": info})


def enable_optimized_write():
    """Add Auto compaction and Optimized writes.
    https://docs.databricks.com/en/delta/tune-file-size.html#auto-compaction-for-delta-lake-on-databricks
    """
    get_spark().conf.set("spark.databricks.delta.autoCompact.enabled", "auto")
    get_spark().conf.set("spark.databricks.delta.optimizeWrite.enabled", True)
