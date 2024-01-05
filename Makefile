env:
	# brew install pyenv
	pip install -U poetry=="1.7.*"
	pyenv install --skip-existing 3.10
	pyenv local 3.10 && poetry env use $(shell pyenv which python3) && poetry install --no-interaction
	poetry run pip install --upgrade pip

env_rm:
	yes | poetry cache clear . --all && poetry env remove --all

fmt:
	# show changes
	poetry run isort --diff --color ./src
	poetry run black --diff --color ./src
	# change
	poetry run isort ./src
	poetry run black ./src

checks:
	poetry run isort --check ./src
	poetry run black --check ./src
	poetry run mypy ./src
	poetry run pylint ./src

#pytest_ci:
#	poetry run pytest -sv --junit-xml junit/test-results.xml ./tests
#
#pytest:
#	poetry run pytest --cache-clear --capture=no --verbose --disable-warnings --color=yes ./tests

#checks_all: checks pytest

lib:
	# 'sdist' for notebooks, 'wheel' for jobs
	poetry build
	ls -1 ./dist

lib_upload: lib
	poetry run python3 src/scripts/upload_lib.py

notebooks_upload:
	poetry run python3 src/scripts/upload_notebooks.py

jobs_create:
	# find ./src/jobs -type f -name "*.py" ! -name "__init__.*" -exec echo {} \; -exec poetry run python3 {} \; -exec echo \;
	find ./src/jobs -type f -name "*.py" ! -name "__init__.*" -print0 | xargs --null -n1 poetry run python3

clean:
	rm -rf ./.*_cache ./dist ./.python-version
	find ./ -type d -name "__pycache__" -exec rm -rf {} +
