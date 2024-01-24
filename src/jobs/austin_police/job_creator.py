import logging
from pathlib import Path

from databricks.sdk.service import jobs

from src.lib.job import BaseDatabricksJob


LOGGER = logging.getLogger(__name__)


# raw
POLICE_CODES_NB_RAW = Path("/main/raw/get_raw_austin_pd_codes")
CRIMES_NB_RAW = Path("/main/raw/get_raw_austin_pd_crimes")
# bronze
POLICE_CODES_NB_BRONZE = Path("/main/bronze/read_austin_pd_codes")
CRIMES_NB_BRONZE = Path("/main/bronze/read_austin_pd_crimes")
# silver
ENRICH_NB_SILVER = Path("/main/silver/enrich_pd_crimes")


class JobCreator(BaseDatabricksJob):
    JOB_NAME = "Austin Police Department crimes"

    def __init__(self):
        super().__init__()
        # Create tasks
        # raw
        police_codes_raw_task = self.create_base_task(POLICE_CODES_NB_RAW)
        crimes_raw_task = self.create_base_task(CRIMES_NB_RAW, max_retries=1, min_retry_interval_millis=60_000)
        # bronze
        police_codes_bronze_task = self.create_base_task(POLICE_CODES_NB_BRONZE)
        crimes_bronze_task = self.create_base_task(CRIMES_NB_BRONZE)
        # silver
        enrich_silver_task = self.create_base_task(ENRICH_NB_SILVER)

        # Make dependencies
        police_codes_bronze_task.depends_on = [jobs.TaskDependency(task_key=police_codes_raw_task.task_key)]
        crimes_bronze_task.depends_on = [jobs.TaskDependency(task_key=crimes_raw_task.task_key)]
        enrich_silver_task.depends_on = [
            jobs.TaskDependency(task_key=police_codes_bronze_task.task_key),
            jobs.TaskDependency(task_key=crimes_bronze_task.task_key),
        ]

        # Make job
        self.job = jobs.JobSettings(
            name=self.JOB_NAME,
            tasks=[
                police_codes_raw_task,
                police_codes_bronze_task,
                crimes_raw_task,
                crimes_bronze_task,
                enrich_silver_task,
            ],
            max_concurrent_runs=1,
            timeout_seconds=0,
        )


def main():
    """Main entry"""
    JobCreator().deploy()


if __name__ == "__main__":
    main()
