import logging
from dataclasses import fields

from databricks.sdk import WorkspaceClient
from databricks.sdk.service import iam, jobs


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


def update_job_permissions_for_users(
    client: WorkspaceClient, job_id: int, permission_level: iam.PermissionLevel = iam.PermissionLevel.CAN_MANAGE
) -> None:
    """Update job permissions for group_name="users" for provided Job ID.

    :param client: Databricks Workspace Client
    :param job_id: Job ID
    :param permission_level: Permission for users for a job
    """
    LOGGER.info(f"Update job permissions for JobID '{job_id}' for group 'users' to '{permission_level}'")
    client.jobs.update_permissions(
        job_id=str(job_id),
        access_control_list=[iam.AccessControlRequest(group_name="users", permission_level=permission_level)],
    )
