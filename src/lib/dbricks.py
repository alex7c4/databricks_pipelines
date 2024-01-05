"""Module with Databricks related helpers"""
from unittest.mock import MagicMock

from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv


def get_databricks_client(**kwargs) -> WorkspaceClient:
    """Load .env file and return WorkspaceClient

    :param kwargs: kwargs passed to WorkspaceClient
    :return: databricks.sdk WorkspaceClient
    """
    load_dotenv()
    return WorkspaceClient(**kwargs)


def get_dbutils():
    """Get `dbutils` if in Databricks environment, or just mock if running locally"""

    class Widgets:
        """`dbutils.widgets` methods mock"""

        text = MagicMock()
        get = MagicMock(return_value="")

    class DButils:
        """`dbutils.widgets` mock"""

        widgets = Widgets()

    try:
        from dbruntime import UserNamespaceInitializer  # pylint: disable=unused-import
    except ModuleNotFoundError:
        _dbutils = DButils()
    else:
        from databricks.sdk.runtime import dbutils

        _dbutils = dbutils  # pylint: disable=redefined-variable-type
    return _dbutils


def widget_text(name: str, default: str = "") -> str:
    """Get widget text value"""
    widgets = get_dbutils().widgets
    widgets.text(name=name, defaultValue=default)
    value: str = widgets.get(name)
    return value
