from pathlib import Path


def test_application_modules_do_not_exceed_one_hundred_lines() -> None:
    application_directory = (
        Path(__file__).resolve().parents[2] / "scout" / "application"
    )
    modules = sorted(application_directory.glob("*.py"))

    assert modules, "Expected at least one application module."

    oversized_modules: dict[str, int] = {}
    for module in modules:
        line_count = len(module.read_text(encoding="utf-8").splitlines())
        if line_count > 100:
            name = module.relative_to(application_directory).as_posix()
            oversized_modules[name] = line_count

    assert not oversized_modules, (
        "Application modules must remain at or below 100 lines: "
        f"{oversized_modules}"
    )
