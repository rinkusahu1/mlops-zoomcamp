# install pi test only for dev env

pipenv install --dev pytest

# search for which interpreter to use
ctrl+shift+p
pipenv --venv

# install deepdiff for result comparison in integration testing


# install linters code analysis tools
pipenv install --dev pylint

pylint model.py

pylint --recursive=y .



```
    TO install all setup run
        make setup
    To test and deploy run
        make publish
```