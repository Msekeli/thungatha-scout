# Thungatha Scout — Development Commands

A quick reference for the commands used during local development. Commands are grouped by the directory from which they should be run.

## 1. Open the project

From a new terminal:

```bash
cd /Users/admin/Documents/Projects/thungatha-scout
```

## 2. Activate the Python virtual environment

The virtual environment is stored in the repository root as `.venv/`, not inside `backend/`.

From the repository root:

```bash
source .venv/bin/activate
```

Then move into the backend directory:

```bash
cd backend
```

Alternatively, if the terminal is already in `backend/`, activate it with:

```bash
source ../.venv/bin/activate
```

When activation succeeds, the terminal prompt normally shows `(.venv)`. This makes the project's Python interpreter and installed packages available to commands such as `python`, `pip` and `pytest`.

To leave the virtual environment:

```bash
deactivate
```

**Important:** `.venv` is the Python virtual environment. `.env` is a separate file that stores environment-variable configuration. Do not confuse the two. The repository documentation confirms that the backend uses Pydantic settings, but the exact `.env` loading configuration/command has not been verified from the source files available when this guide was prepared. Do not run `source .env` by assumption; confirm the settings configuration first.

## 3. Install or update Python dependencies

Run these from `backend/` with the virtual environment activated.

Install the backend requirements file:

```bash
python -m pip install -r requirements.txt
```

The project has also used the editable install with development, crawler and AI extras:

```bash
python -m pip install -e ".[dev,crawler,ai]"
```

Check for dependency conflicts:

```bash
python -m pip check
```

Inspect an installed package:

```bash
python -m pip show PACKAGE_NAME
```

Replace `PACKAGE_NAME` with the package to inspect, for example `playwright` or `google-genai`.

## 4. Run database migrations

Run from `backend/` with the virtual environment activated:

```bash
python -m scout.persistence.migration_runner
```

This runs the project's migration runner. Use this instead of manually running migration SQL with `psql` unless a task specifically requires that.

## 5. Import registry data

Run from `backend/` with the virtual environment activated:

```bash
python -m scout.registry_importer
```

Run the migration runner before the registry importer when both are required.

## 6. Run Python tests

Run commands from `backend/` with the virtual environment activated.

Run the complete unit-test suite:

```bash
python -m pytest test-suites/unit-tests -q
```

Run all tests discovered by the project's pytest configuration (unit and integration test paths):

```bash
python -m pytest -q
```

Run one test file:

```bash
python -m pytest test-suites/unit-tests/PATH_TO_TEST_FILE.py -q
```

Run one test directory, for example the Lever adapter tests:

```bash
python -m pytest test-suites/unit-tests/ats-adapters/lever-adapter -q
```

Run a specific test module, for example settings tests:

```bash
python -m pytest test-suites/unit-tests/test_settings.py -q
```

`-q` means quiet output. Remove `-q` when more detailed test output is useful.

## 7. Run Python linting and formatting checks

Run from `backend/` with the virtual environment activated.

Check Python code with Ruff:

```bash
ruff check scout test-suites
```

Check whether files are already formatted:

```bash
ruff format --check scout test-suites
```

Apply Ruff formatting (this changes files):

```bash
ruff format scout test-suites
```

## 8. Run repository-wide required checks

These scripts are run from the repository root, not from `backend/`:

```bash
python3 scripts/check-file-line-limits.py
python3 scripts/check-naming-conventions.py
```

They check the repository's file-length and naming rules.

## 9. Frontend checks

These are Node/npm commands, not Python commands. Run from `frontend/`:

```bash
npm run typecheck
npm run build
npm run test:contracts
```

## 10. Typical backend session

For a normal backend development session, the sequence is:

```bash
cd /Users/admin/Documents/Projects/thungatha-scout
source .venv/bin/activate
cd backend
python -m scout.persistence.migration_runner
python -m pytest test-suites/unit-tests -q
ruff check scout test-suites
ruff format --check scout test-suites
```

Only run migrations when there are unapplied migrations. Run the registry importer when registry data needs to be imported or refreshed.

## Notes

- Never commit `.env`, credentials, tokens or other secrets.
- Do not put secrets in frontend environment variables. Backend service-role credentials must remain server-side.
- Prefer `python -m ...` for Python modules so the command uses the active virtual environment's interpreter.
- If a command fails because a package is missing, confirm that `(.venv)` is active before installing anything.
- The exact local FastAPI/Uvicorn start command is intentionally not listed here because it was not verified against the current backend entry point and configuration.
