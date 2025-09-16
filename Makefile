.PHONY: all lint

all: help

lint:
	uv run ruff check . --fix
	uv run ruff format .
