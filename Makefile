# from https://pcjedi.github.io/2025/11/23/the-purpose-of-makefile.html

compose ?= podman-compose
UV_VENV_CLEAR ?= 1

export

.PHONY: all
all: rpm

requirements-%.txt: pyproject.toml
	uv pip compile --group $* --format requirements.txt --output-file $@ pyproject.toml


requirements.txt: pyproject.toml
	uv pip compile --format requirements.txt --output-file requirements.txt pyproject.toml

pylock.toml: pyproject.toml
	uv pip compile --format pylock.toml --output-file pylock.toml pyproject.toml

uv.lock: pyproject.toml
	uv lock

pyproject.toml:
	uv init
	uv add ipykernel --group dev
	uv add pyyaml

dist: pyproject.toml
	uv build --package xen_sysmon

.PHONY: test
test:
	uv run python -m pytest


.venv: uv.lock
	uv venv
	uv sync

install: .venv
	uv pip install .

sh:
	$(compose) run --no-build --rm

.PHONY: rpm
rpm: | test clean
	$(compose) up --no-build --remove-orphans --force-recreate

.PHONY: rpmspec
rpmspec pkg/python-xen-sysmon.spec pkg/python-xen-sysmon.conf: dist install
	pyp2spec -a xen_sysmon --path ./dist
	mv python-xen-sysmon.* dist/

.PHONY: clean distclean
clean:  ## Clean up cache files and build artifacts
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ \
		.mypy_cache/ uv.lock pylock.toml \
		requirements*.txt *.whl python-*.spec python-*.conf

distclean: clean
	rm -rf .rpmbuild/ .venv/
