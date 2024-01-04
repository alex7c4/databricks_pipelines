"""
Read and process raw austin police report JSON files to the bronze table.
"""
import pyspark.sql.functions as F
import pyspark.sql.types as T

from src.lib.common_cfg import RAW_SAVE_PATH
from src.lib.spark import comment, enable_optimized_write, get_spark


# COMMAND ----------

RESULT_TABLE = "bronze.austin_pd_crime_records"
RAW_FILES_PATH = RAW_SAVE_PATH / "austin_pd_crimes" / "austin_pd_crime_reports_*.json"

# COMMAND ----------

# Read raw files
spark = get_spark()

schema = T.StructType(
    [
        T.StructField("address", T.StringType()),
        T.StructField("category_description", T.StringType()),
        T.StructField("census_tract", T.StringType()),
        T.StructField("clearance_date", T.StringType()),
        T.StructField("clearance_status", T.StringType()),
        T.StructField("council_district", T.StringType()),
        T.StructField("crime_type", T.StringType()),
        T.StructField("district", T.StringType()),
        T.StructField("family_violence", T.StringType()),
        T.StructField("incident_report_number", T.StringType()),
        T.StructField("latitude", T.StringType()),
        T.StructField(
            "location",
            T.StructType(
                [
                    T.StructField("human_address", T.StringType()),
                    T.StructField("latitude", T.StringType()),
                    T.StructField("longitude", T.StringType()),
                ]
            ),
        ),
        T.StructField("location_type", T.StringType()),
        T.StructField("longitude", T.StringType()),
        T.StructField("occ_date", T.StringType()),
        T.StructField("occ_date_time", T.StringType()),
        T.StructField("occ_time", T.StringType()),
        T.StructField("pra", T.StringType()),
        T.StructField("rep_date", T.StringType()),
        T.StructField("rep_date_time", T.StringType()),
        T.StructField("rep_time", T.StringType()),
        T.StructField("sector", T.StringType()),
        T.StructField("ucr_category", T.StringType()),
        T.StructField("ucr_code", T.StringType()),
        T.StructField("x_coordinate", T.StringType()),
        T.StructField("y_coordinate", T.StringType()),
        T.StructField("zip_code", T.StringType()),
    ]
)

data_df = spark.read.json(path=RAW_FILES_PATH.as_posix(), multiLine=True, schema=schema, mode="FAILFAST")

# COMMAND ----------

# Fix types
new_data_df = (
    data_df
    .select(
        F.col("incident_report_number").cast("long"),
        F.to_date("rep_date").alias("rep_date"),
        F.to_timestamp("rep_date_time").alias("rep_date_time"),
        F.col("rep_time").cast("int"),
        "crime_type",
        "ucr_category",
        F.col("ucr_code").cast("int"),
        "category_description",
        (
            F.when(F.lower("family_violence") == "y", value=True)
            .when(F.lower("family_violence") == "n", value=False)
            .otherwise(F.lit(None))
        ).cast("boolean").alias("family_violence"),
        "address",
        "location_type",
        F.col("council_district").cast("int"),
        F.col("district").cast("int"),
        "sector",
        F.col("zip_code").cast("int"),
        F.col("census_tract").cast("float"),
        F.to_date("clearance_date").alias("clearance_date"),
        "clearance_status",
        F.to_date("occ_date").alias("occ_date"),
        F.to_timestamp("occ_date_time").alias("occ_date_time"),
        F.col("occ_time").cast("int"),
        F.col("pra").cast("int"),
        F.col("x_coordinate").cast("int"),
        F.col("y_coordinate").cast("int"),
        F.col("latitude").cast("float"),
        F.col("longitude").cast("float"),
        # 'location',
    )
    .orderBy(F.desc("rep_date_time"))
)

# COMMAND ----------

# Add comments
new_data_df = (
    new_data_df
    .select(
        comment("incident_report_number", "Incident report number"),
        comment("rep_date", "Date the incident was reported"),
        comment("rep_date_time", "Date and time incident was reported"),
        comment("rep_time", "Time the incident was reported"),
        comment("crime_type", "Highest Offense Description"),
        comment(
            "ucr_category",
            "Code for the most serious crimes identified by the FBI as part of its Uniform Crime Reporting program",
        ),
        comment("ucr_code", "Highest Offense Code"),
        comment(
            "category_description",
            "Description for the most serious crimes identified by the FBI as part of its Uniform Crime Reporting program",
        ),
        comment("family_violence", "Incident involves family violence?"),
        comment("address", "Incident location"),
        comment("location_type", "General description of the premise where the incident occurred"),
        comment("council_district", "Austin city council district where incident occurred"),
        comment("district", "APD district where incident occurred"),
        comment("sector", "APD sector where incident occurred"),
        comment("pra", "APD police reporting area where incident occurred"),
        comment("zip_code", "Zip code where incident occurred"),
        comment("census_tract", "Census tract where incident occurred"),
        comment("clearance_date", "Date crime was solved"),
        comment("clearance_status", "How/whether crime was solved"),
        comment("occ_date", "Date the incident occurred"),
        comment("occ_date_time", "Date and time incident occurred"),
        comment("occ_time", "Time the incident occurred"),
        comment("x_coordinate", "X-coordinate where the incident occurred"),
        comment("y_coordinate", "Y-coordinate where incident occurred"),
        comment("latitude", "Latitude where incident occurred"),
        comment("longitude", "Longitude where the incident occurred"),
    )
    .orderBy(F.desc("rep_date_time"))
)

# COMMAND ----------

# Write
enable_optimized_write()

spark.sql("CREATE SCHEMA IF NOT EXISTS bronze")
# spark.sql(f"DROP TABLE IF EXISTS {RESULT_TABLE}")

(
    new_data_df
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", True)
    .saveAsTable(RESULT_TABLE)
)

spark.sql(f"OPTIMIZE {RESULT_TABLE} ZORDER BY (rep_date, ucr_code, crime_type)")
spark.sql(f"VACUUM {RESULT_TABLE}")
