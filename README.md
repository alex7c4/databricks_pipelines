[![Check and Upload to Databricks](https://github.com/alex7c4/databricks_pipelines/actions/workflows/deploy.yml/badge.svg?branch=master)](https://github.com/alex7c4/databricks_pipelines/actions/workflows/deploy.yml)

Training project to make Databricks pipelines.

CI _(GitHub Actions)_ will run checks, tests and deploy the notebooks to the Databricks server and Prefect Flows to a Prefect Cloud.

> [!NOTE]
> This project is still in WIP

---
### Pre-requirements

Following things will be needed:
- [Azure](https://portal.azure.com/) account (For _'Azure Databricks'_ and _'Azure Blob Storage'_)

### Setup environment

1) Setup Azure Databricks and create token for your account.
2) Create container `flows` in Azure Storage.
3) Prepare `.env` file from an [`.env_template`](.env_template): `cp .env_template .env` and fill your secrets.


### CI flow
GitHub Actions CI/CD flow defined under [`.github/workflows`](.github/workflows):
```mermaid
---
title: CI flow
---
flowchart LR

    subgraph pr[Pull request flow]
    direction TB
        A1[Install Python and dependencies] -->
        B1[Static checks] -->
        C1[Unit tests] -->
        D1[Upload test results]
    end

    subgraph deploy[Merge to master flow]
    direction TB
        A2[Upload notebooks to Databricks] -->
        B2[Build and upload Python lib to Databricks] -->
        C2[Deploy Prefect Flows to Prefect Cloud]
    end

    pr --> deploy
```
