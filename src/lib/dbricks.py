"""Module with Databricks related helpers"""

import py4j
from databricks.sdk import WorkspaceClient
from databricks.sdk.dbutils import RemoteDbUtils
from databricks.sdk.runtime import dbutils
from dotenv import load_dotenv


def get_databricks_client(**kwargs) -> WorkspaceClient:
    """Load .env file and return WorkspaceClient

    :param kwargs: kwargs passed to WorkspaceClient
    :return: databricks.sdk WorkspaceClient
    """
    load_dotenv()
    return WorkspaceClient(**kwargs)


def get_dbutils() -> RemoteDbUtils:
    """Get `dbutils` if in Databricks environment, or just mock if running locally"""
    return dbutils


def widget_get_str(name: str, default: str) -> str:
    """Get a string widget value. If widget is not defined - default value will be set.

    :param name: Widget name.
    :param default: Default value.
    :return: Str value
    """
    try:
        val: str = dbutils.widgets.get(name)
    except (py4j.protocol.Py4JJavaError, KeyError) as e:
        if "InputWidgetNotDefined" in e.java_exception.toString():  # type: ignore
            dbutils.widgets.text(name, default)  # set widget
            val: str = dbutils.widgets.get(name)  # type: ignore[no-redef]
        else:
            raise
    val = val.strip()  # type: ignore[no-redef]
    print(f"Widget val: '{name}' = '{val}'")
    return val
