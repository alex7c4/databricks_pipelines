# Databricks notebook source
from src.lib.dbricks import widget_text


class Config:
    name = widget_text("name")
    value = widget_text("value")


# COMMAND ----------

print(f"{Config.name=}")
print(f"{Config.value=}")
