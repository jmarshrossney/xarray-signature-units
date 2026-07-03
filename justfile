_: lint typecheck test doctest docs

# Format and lint the package using ruff.
lint:
  ruff format
  ruff check --fix
  marimo check --fix examples/notebook.py

# Variant of `lint` that doesn't cause any changes to files.
lint-check:
  ruff format --check
  ruff check
  marimo check examples/notebook.py

# Run static type checker.
typecheck:
  pyright

# Run the full test suite.
test:
  pytest --verbose

# Run tests with coverage report.
test-cov:
  pytest --cov=xarray_annotated --cov-report=term-missing --cov-fail-under=95

# Run doctest examples embedded in source docstrings.
doctest:
  pytest --doctest-modules src/xarray_annotated --verbose

# Build the documentation using Zensical.
docs:
  marimo-md-export examples/notebook.py docs/example.md
  zensical build
