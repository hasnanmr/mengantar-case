.PHONY: api-dev install build-index

install:
	pip install -e .

api-dev:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

build-index:
	uv run python -m app.rag.knowledge_base

test:
	pytest tests/ -v
