"""Script to upload pipelines to Databricks"""
from pathlib import Path

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.workspace import ImportFormat, Language
from dotenv import load_dotenv


load_dotenv()

NOTEBOOKS_LOCAL_PATH = Path("src/notebooks")


def main():
    """Main logic"""
    # get all py-files under pipelines dir
    notebooks = list(NOTEBOOKS_LOCAL_PATH.rglob("*.py"))
    if not notebooks:
        raise ValueError("No notebooks")

    workspace_client = WorkspaceClient()

    # prepare future Databricks' directory full path
    py_files_dirs = [(Path("/main") / x.parent.relative_to(NOTEBOOKS_LOCAL_PATH), x) for x in notebooks]

    # create directory in databricks
    for db_dir in {x[0] for x in py_files_dirs}:
        print(f"Creating remote directory: '{db_dir}'")
        workspace_client.workspace.mkdirs(path=db_dir.as_posix())

    # upload notebook
    for db_dir, local_file_path in py_files_dirs:
        print(f"Uploading: '{local_file_path}'")
        workspace_client.workspace.upload(
            path=(db_dir / local_file_path.stem).as_posix(),
            content=local_file_path.read_bytes(),
            format=ImportFormat.SOURCE,
            language=Language.PYTHON,
            overwrite=True,
        )


if __name__ == "__main__":
    main()
    print("--DONE--")
