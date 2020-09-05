.PHONY: all clean test

clean:
	rm -rf coverage
	rm -rf dist
	rm -rf build

test-code:
	pytest docomp

test-coverage:
	rm -rf coverage .coverage
	pytest --cov=docomp docomp

test: test-coverage

code-format:
	black -S docomp

code-analysis:
	flake8 docomp --max-line-length=88
	pylint -E docomp/ -d E1103,E0611,E1101
