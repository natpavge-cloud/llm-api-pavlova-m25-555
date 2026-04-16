install:
	uv sync

run:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

lock:
	uv lock

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check . --fix

build:
	uv build

package-install:
	python -m pip install dist/*.whl
	