"""Script to build and upload 'pipelines_lib'"""
from pathlib import Path
from pprint import pprint

from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv


load_dotenv()

UPLOAD_TARGET_DIR = Path("dbfs:/libs/databricks_pipelines/main")
LOCAL_LIB_PATH = Path("./dist/")


def main():
    """Main logic"""
    libs_paths = list(LOCAL_LIB_PATH.glob("databricks_pipelines-*"))
    if not libs_paths:
        raise ValueError("No local libs")

    workspace_client = WorkspaceClient()

    for f_path in libs_paths:
        upload_path = UPLOAD_TARGET_DIR / f_path.name
        print(f"\nUploading '{f_path}' to '{upload_path}'")
        with f_path.open(mode="rb") as fileo:
            workspace_client.dbfs.upload(path=upload_path.as_posix(), src=fileo, overwrite=True)

        pprint(list(workspace_client.dbfs.list(path=upload_path.as_posix(), recursive=True)))


if __name__ == "__main__":
    main()
    print("--DONE--")
