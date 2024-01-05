import logging
from pathlib import Path

from databricks.sdk.service import jobs

from src.lib.clusters import BaseCluster, BaseLib
from src.lib.dbricks import get_databricks_client
from src.lib.job import create_or_update_job


LOGGER = logging.getLogger(__name__)

JOB_NAME = "Austin Police Department crimes"

# raw level
POLICE_CODES_NB_RAW = Path("/master/0_raw/get_raw_austin_pd_codes")
CRIMES_NB_RAW = Path("/master/0_raw/get_raw_austin_pd_crimes")
# bronze level
POLICE_CODES_NB_BRONZE = Path("/master/1_bronze/read_austin_pd_codes")
CRIMES_NB_BRONZE = Path("/master/1_bronze/read_austin_pd_crimes")


def create_task(notebook_path: Path) -> jobs.Task:
    """Create task.

    :param notebook_path: Path to the existing notebook inside Databricks.
    :return: Task
    """
    return jobs.Task(
        notebook_task=jobs.NotebookTask(
            notebook_path=notebook_path.as_posix(),
            source=jobs.Source.WORKSPACE,
        ),
        task_key=notebook_path.name,
        run_if=jobs.RunIf.ALL_SUCCESS,
        timeout_seconds=0,
        new_cluster=BaseCluster(),
        libraries=[BaseLib()],
    )


def main():
    """Main entry"""
    workspace_client = get_databricks_client()

    police_codes_raw_task = create_task(POLICE_CODES_NB_RAW)
    police_codes_bronze_task = create_task(POLICE_CODES_NB_BRONZE)
    crimes_raw_task = create_task(CRIMES_NB_RAW)
    crimes_bronze_task = create_task(CRIMES_NB_BRONZE)

    police_codes_bronze_task.depends_on = [jobs.TaskDependency(task_key=police_codes_raw_task.task_key)]
    crimes_bronze_task.depends_on = [jobs.TaskDependency(task_key=crimes_raw_task.task_key)]

    job = jobs.JobSettings(
        name=JOB_NAME,
        tasks=[
            police_codes_raw_task,
            police_codes_bronze_task,
            crimes_raw_task,
            crimes_bronze_task,
        ],
        max_concurrent_runs=1,
        timeout_seconds=0,
    )

    # create
    job_id = create_or_update_job(client=workspace_client, job_settings=job)
    LOGGER.info(f"JobID: {job_id}")


if __name__ == "__main__":
    main()
