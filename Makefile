release:
	git tag -a `python setup.py --version` -m "Releasing to https://pypi.python.org/pypi/flask-restful-swagger-2/"
	git push --tags
	python setup.py sdist
	twine upload dist/*
