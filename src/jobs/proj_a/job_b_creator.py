import logging

from databricks.sdk.service import jobs

from src.lib.clusters import BaseCluster, BaseLib
from src.lib.data_structures import JobParams
from src.lib.dbricks import get_databricks_client
from src.lib.job import create_or_update_job


LOGGER = logging.getLogger(__name__)


PARAMS = (
    JobParams(source_table="e1", target_table="e2"),
    JobParams(source_table="f1", target_table="f2"),
    JobParams(source_table="j1", target_table="j2"),
)


JOB_NAME = "Job B"
NOTEBOOK_PATH = "/Users/prived007@gmail.com/proj_a/dummy_notebook"


def main():
    """Main entry"""
    workspace_client = get_databricks_client()

    tasks = []
    for param in PARAMS:
        tasks.append(
            jobs.Task(
                notebook_task=jobs.NotebookTask(
                    notebook_path=NOTEBOOK_PATH,
                    source=jobs.Source.WORKSPACE,
                    base_parameters={"name": param.source_table, "value": param.target_table},
                ),
                task_key=f"task_{param.source_table}_to_{param.target_table}",
                run_if=jobs.RunIf.ALL_SUCCESS,
                timeout_seconds=0,
                new_cluster=BaseCluster(),
                libraries=[BaseLib()],
            )
        )

    # chain tasks
    for idx in range(0, len(tasks) - 1):
        tasks[idx].depends_on = [jobs.TaskDependency(task_key=tasks[idx + 1].task_key)]

    job = jobs.JobSettings(name=JOB_NAME, tasks=tasks, max_concurrent_runs=1, timeout_seconds=0)

    # create
    job_id = create_or_update_job(client=workspace_client, job_settings=job)
    LOGGER.info(f"JobID: {job_id}")


if __name__ == "__main__":
    main()
