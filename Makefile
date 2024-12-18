.PHONY: all init run-bge run-bge-finetuned format lock

init:
	uv sync

run:
    uv run main.py

format:
	uv run ruff format
	uv run ruff check --fix

lock:
	uv lock
	uv export > requirements.txt