.PHONY: api-dev install build-index

install:
	pip install -e .

api-dev:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

build-index:
	python -m app.rag.build_index

test:
	pytest tests/ -v
