shell:
	docker run -it --rm -v $(PWD):/w -w /w python:3.11 bash

lint:
	python setup.py flake8

test:
	python setup.py test

release:
	python setup.py sdist bdist_wheel
	twine upload dist/*
