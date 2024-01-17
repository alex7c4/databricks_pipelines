[![Check and Upload to Databricks](https://github.com/alex7c4/databricks_pipelines/actions/workflows/deploy.yml/badge.svg?branch=master)](https://github.com/alex7c4/databricks_pipelines/actions/workflows/deploy.yml)

Training project to make Databricks pipelines.

CI _(GitHub Actions)_ will run checks, tests and deploy notebooks and jobs to the Databricks server.

> [!NOTE]
> This project is still in WIP

### Databricks Jobs
Here are approximate Databricks Jobs dependencies:

```mermaid
flowchart LR
    classDef raw fill:#949494
    classDef bronze fill:#CD7F32
    classDef silver fill:#e0e0e0

    r1(Raw Job 1):::raw
    r2(Raw Job 2):::raw
    b1(Bronze Job 1):::bronze
    b2(Bronze Job 2):::bronze
    s1(Silver Job):::silver

    r1 --> b1
    r2 --> b2
    b1 & b2 --> s1
```

---

### Setup environment

1) Setup Azure Databricks and create token for your account.
2) Prepare `.env` file from an [`.env_template`](.env_template): `cp .env_template .env` and fill your secrets.


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
        C1[TODO: Unit tests] -->
        D1[TODO: Upload test results]
    end

    subgraph deploy[Merge to master flow]
    direction TB
        A2[Upload notebooks to Databricks] -->
        B2[Build and upload Python lib to Databricks] -->
        C2[Create Databricks Jobs]
    end

    pr --> deploy
```
