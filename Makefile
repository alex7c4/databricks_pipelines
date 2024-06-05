env:
	# brew install pyenv
	pip install -U poetry=="1.8.*"
	pyenv install --skip-existing 3.11
	poetry env use $(shell pyenv local 3.11 && pyenv which python3) && poetry install --no-interaction
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
#	poetry run pylint ./src

#pytest_ci:
#	poetry run pytest -sv --junit-xml junit/test-results.xml ./tests
#
#pytest:
#	poetry run pytest --cache-clear --capture=no --verbose --disable-warnings --color=yes ./tests

#checks_all: checks pytest

clean:
	rm -rf ./.*_cache ./dist ./.python-version
	find ./ -type d -name "__pycache__" -exec rm -rf {} +
