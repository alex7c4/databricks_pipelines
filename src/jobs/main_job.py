import logging
import random
import string
from collections.abc import Iterable

from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs

from src.jobs import proj_a
from src.lib.dbricks import get_databricks_client
from src.lib.job import create_or_update_job, get_check_existing_job


LOGGER = logging.getLogger(__name__)


JOB_NAME = "One job to rule them all"

PROJ_A_JOBS = (proj_a.job_a_name, proj_a.job_b_name)
PROJ_B_JOBS = (proj_a.job_a_name, proj_a.job_b_name)


def make_tasks(client: WorkspaceClient, jobs_names: Iterable[str]) -> list[jobs.Task]:
    """Make tasks from Job Names.

    :param client: Databricks Workspace Client
    :param jobs_names: Job Names to make tasks from them
    :return: List of jobs.Task objects
    """
    tasks = []
    for job_name in jobs_names:
        tasks.append(
            jobs.Task(
                run_job_task=jobs.RunJobTask(job_id=get_check_existing_job(client=client, job_name=job_name).job_id),
                task_key=f"{job_name.replace(' ', '_')}__{random.choice(string.ascii_lowercase)}",
                run_if=jobs.RunIf.ALL_SUCCESS,
                timeout_seconds=0,
            )
        )
    return tasks


def chain_tasks(tasks: list[jobs.Task]):
    """Chain tasks from provided list. Updates will be done in-place."""
    for idx in range(0, len(tasks) - 1):
        tasks[idx].depends_on = [jobs.TaskDependency(task_key=tasks[idx + 1].task_key)]


def main():
    """Main job"""
    workspace_client = get_databricks_client()

    proj_a_tasks = make_tasks(workspace_client, PROJ_A_JOBS)
    proj_b_tasks = make_tasks(workspace_client, PROJ_B_JOBS)

    # chain tasks
    chain_tasks(proj_a_tasks)
    chain_tasks(proj_b_tasks)

    # make jobs for proj_a
    job_id = create_or_update_job(
        client=workspace_client,
        job_settings=jobs.JobSettings(
            name=JOB_NAME,
            tasks=proj_a_tasks + proj_b_tasks,
            max_concurrent_runs=1,
            timeout_seconds=0,
        ),
    )

    LOGGER.info(f"JobIDs: {job_id}")


if __name__ == "__main__":
    main()
