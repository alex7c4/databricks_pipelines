import logging
from dataclasses import fields
from pathlib import Path

from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs

from src.lib.clusters import BaseCluster, BaseLib
from src.lib.dbricks import get_databricks_client

from src.lib.clusters import BaseCluster, BaseLib
from src.lib.dbricks import get_databricks_client


LOGGER = logging.getLogger(__name__)


def get_existing_job(client: WorkspaceClient, job_name: str) -> None | jobs.Job:
    """Get most resent existing job fully matched with provided 'job_name'.
    May be problems if you have more than 100 jobs with the same name.

    :param client: Databricks Workspace Client
    :param job_name: Name of the job to search
    :return: Job info if job found, otherwise None
    """
    # get first 100 jobs fully matching provided name
    existing_jobs = sorted(client.jobs.list(name=job_name, limit=100), key=lambda x: x.created_time, reverse=True)
    if existing_jobs:
        return client.jobs.get(job_id=existing_jobs[0].job_id)
    return None


def get_check_existing_job(client: WorkspaceClient, job_name: str) -> jobs.Job:
    """Get most resent existing job fully matched with provided 'job_name'.
    May be problems if you have more than 100 jobs with the same name.

    :param client: Databricks Workspace Client
    :param job_name: Name of the job to search
    :return: Job info if job found, otherwise None
    """
    job = get_existing_job(client=client, job_name=job_name)
    if not job:
        raise ValueError(f"Job with name '{job_name}' is missing")
    return job


def update_job(client: WorkspaceClient, job_id: int, job_setting: jobs.JobSettings) -> int:
    """Update existing job with new JobSettings.

    :param client: Databricks Workspace Client
    :param job_id: Existing Job ID
    :param job_setting: New job settings
    :return: Job ID
    """
    LOGGER.info(f"Update existing JobID '{job_id}'")
    client.jobs.reset(job_id=job_id, new_settings=job_setting)
    return job_id


def create_job(client: WorkspaceClient, job_setting: jobs.JobSettings) -> int:
    """Create new job.

    :param client: Databricks Workspace Client
    :param job_setting: job settings
    :return: Job ID
    """
    LOGGER.info("Create new job")
    response = client.jobs.create(**{_field.name: getattr(job_setting, _field.name) for _field in fields(job_setting)})
    job_id: int = response.job_id
    return job_id


def create_or_update_job(client: WorkspaceClient, job_settings: jobs.JobSettings) -> int:
    """Create new job (if not exist) or update existing.

    :param client: Databricks Workspace Client
    :param job_settings: Job settings
    :return: Job ID
    """
    existing_job = get_existing_job(client, job_name=job_settings.name)
    if existing_job:
        # update existing job with provided job settings
        job_id = update_job(client, job_id=existing_job.job_id, job_setting=job_settings)
    else:
        # create new job
        job_id = create_job(client, job_setting=job_settings)
    return job_id


class BaseDatabricksJob:
    JOB_NAME: str = None

    def __init__(self):
        self.workspace_client = get_databricks_client()
        self.job: jobs.JobSettings = None

    @staticmethod
    def create_base_task(notebook_path: Path, **kwargs) -> jobs.Task:
        """Create task.

        :param notebook_path: Path to the existing notebook inside Databricks.
        :param kwargs: Params to pass to the 'jobs.Task'
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
            **kwargs,
        )

    def deploy(self) -> int:
        """Deploy job to Databricks.

        :return: Job ID of created or updated job
        """
        job_id = create_or_update_job(client=self.workspace_client, job_settings=self.job)
        LOGGER.info(f"Job ID '{job_id}' deployed to Databricks")
        return job_id
