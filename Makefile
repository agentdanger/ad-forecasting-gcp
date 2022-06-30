setup:
	python -m venv ./venv

install:
	pip install -r requirements.txt

test:
	python -m pytest -vv --cov=myrepolib tests/

lint:
	pylint --disable=R,C myrepolib  

lint2:
	pylint --disable=R,C tests

all: install lint lint2 test