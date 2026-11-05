from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
CHECKER_PATH = REPOSITORY_ROOT / "scripts" / "check-file-line-limits.py"
SPEC = spec_from_file_location("source_line_limit_checker", CHECKER_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECKER = module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


def test_all_handwritten_source_files_respect_the_line_limit() -> None:
    violations = CHECKER.check_file_line_limits(REPOSITORY_ROOT)
    assert not violations, (
        f"Handwritten source files must remain at or below 100 lines: {violations}"
    )
