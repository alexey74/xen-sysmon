# from https://pcjedi.github.io/2025/11/23/the-purpose-of-makefile.html

compose ?= podman-compose
UV_VENV_CLEAR ?= 1
FEDORA_VER ?= 37
UP_ARGS ?= --remove-orphans --force-recreate

export

.PHONY: all rebuild req wheel wheel-in
all: test rpm

wheel: | clean Dockerfile
	$(compose) run --rm xen-sysmon make wheel-in

wheel-in: requirements.txt pyproject.toml
	pip wheel . -w dist
	cp requirements.txt dist/

rebuild:
	$(MAKE) all UP_ARGS="--build --remove-orphans"

req: requirements.txt requirements-dev.txt

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

.PHONY: test pre-commit
test: pre-commit
	uv run python -m pytest

pre-commit:
	pre-commit run --all-files

.venv: uv.lock
	uv venv
	uv sync

install: .venv
	uv pip install .

sh:
	$(compose) run --rm xen-sysmon bash

.PHONY: rpm
rpm: | clean Dockerfile
	$(compose) up $(UP_ARGS)

.PHONY: rpmspec
rpmspec pkg/python-xen-sysmon.spec pkg/python-xen-sysmon.conf: dist install
	pyp2spec -a xen_sysmon --path ./dist
	mv python-xen-sysmon.* dist/

.PHONY: clean distclean container-clean
clean:  container-clean ## Clean up cache files and build artifacts
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage coverage.xml htmlcov/ .*_cache/ \
		.mypy_cache/ *.whl python-*.spec python-*.conf \
		.rpmbuild/

distclean: clean
	rm -rf .venv/ uv.lock pylock.toml requirements*.txt

container-clean:
	$(compose) down --volumes


c-%:
	$(compose) $* $(A)
