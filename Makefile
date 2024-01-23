.PHONY: requirements install 

install:
	pip-sync requirements.txt

requirements:
	rm -rf requirements.txt
	python -m pip install --upgrade pip pip-tools setuptools wheel
	pip-compile requirements/base.in -o requirements.txt --resolver=backtracking
