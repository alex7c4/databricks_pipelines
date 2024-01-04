from dataclasses import dataclass, field

from databricks.sdk.service import compute


@dataclass
class BaseLib(compute.Library):
    whl: str = "dbfs:/libs/databricks_pipelines/main/databricks_pipelines-0.0.1-py3-none-any.whl"


@dataclass
class BaseCluster(compute.ClusterSpec):
    spark_version: str = "14.2.x-scala2.12"
    node_type_id: str = "Standard_F4"  # 8GB RAM 4CPU
    driver_node_type_id: str = "Standard_F4"
    runtime_engine: compute.RuntimeEngine = compute.RuntimeEngine.STANDARD
    num_workers: int = 0
    spark_conf: dict[str, str] = field(
        default_factory=lambda: {
            "spark.master": "local[*, 4]",
            "spark.databricks.cluster.profile": "singleNode",
        }
    )
    azure_attributes: compute.AzureAttributes = compute.AzureAttributes(
        availability=compute.AzureAvailability.ON_DEMAND_AZURE,
        first_on_demand=1,
        spot_bid_max_price=-1,
    )
    custom_tags: dict[str, str] = field(default_factory=lambda: {"ResourceClass": "SingleNode"})
    spark_env_vars: dict[str, str] = field(
        default_factory=lambda: {"PYSPARK_PYTHON": "/databricks/python3/bin/python3"}
    )
    enable_elastic_disk: bool = True
