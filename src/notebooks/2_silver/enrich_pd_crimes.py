# Databricks notebook source
import os, sys  # isort: skip ; pylint: disable=multiple-imports
sys.path.append(os.environ.get("BUNDLE_SOURCE_PATH", "."))

# COMMAND ----------

# MAGIC %sql select * from bronze.austin_pd_crime_records limit 1000

# COMMAND ----------

# MAGIC %sql select * from bronze.austin_pd_codes

# COMMAND ----------

# MAGIC %sql
# MAGIC select *
# MAGIC from bronze.austin_pd_crime_records r
# MAGIC left join bronze.austin_pd_codes c
# MAGIC   on r.ucr_code = c.apd_code
# MAGIC order by rep_date_time desc
