#!/usr/bin/env python3
"""Enforces repository-wide descriptive folder and file naming rules."""

import sys
from pathlib import Path

PROHIBITED_GENERIC_NAMES = {
    "common", "misc", "helpers", "utils", "services", "types",
    "data", "manager", "processor", "temp", "shared",
}

DOCUMENTED_DIRECTORY_EXCEPTIONS = {
    "src", "ui", "app", "lib", "api", "milestones", "scripts",
    "backend", "frontend", "scout", "domain", "adapters", "persistence",
    "components", "styles", "tests", "unit", "diagnostics", "maintenance",
    "test-suites", "unit-tests", "integration-tests", "registry",
    "database-migrations", "application",
}

DOCUMENTED_FILE_EXCEPTIONS = {
    "main.tsx", "main.py", "App.tsx", "__init__.py", "__main__.py",
    "README.md", "LICENSE", "index.html", "vite.config.ts",
    "tailwind.config.js", "postcss.config.js", "components.json",
    "pyproject.toml", "package.json", "package-lock.json",
    "tsconfig.json", "tsconfig.tsbuildinfo", "vite-env.d.ts",
    "styles.css", "avatar.tsx", "badge.tsx", "button.tsx", "card.tsx",
    "dialog.tsx", "dropdown-menu.tsx", "input.tsx", "label.tsx",
    "select.tsx", "separator.tsx", "sheet.tsx", "skeleton.tsx",
    "table.tsx", "tabs.tsx", "tooltip.tsx", "utils.ts", "textarea.tsx",
    "geography.py", "authentication.py", "settings.py", "vacancies.py",
    "employers.py", "api.ts", "supabase.ts",
}

IGNORED_DIRECTORIES = {
    ".git", ".venv", "node_modules", "dist", "__pycache__",
    ".pytest_cache", ".ruff_cache", ".mypy_cache",
    ".egg-info", "thungatha_scout_backend.egg-info",
}


def check_naming(root_dir: Path) -> list[str]:
    violations: list[str] = []
    scan_roots = [root_dir / "backend", root_dir / "frontend" / "src"]

    for scan_root in scan_roots:
        if not scan_root.exists():
            continue
        for path in scan_root.rglob("*"):
            if any(ignored in path.parts for ignored in IGNORED_DIRECTORIES):
                continue

            name_stem = path.stem.lower()
            name_full = path.name

            # Check directory names as well as source filenames.
            if path.is_dir() and name_full not in DOCUMENTED_DIRECTORY_EXCEPTIONS:
                if "-" not in name_full and "_" not in name_full:
                    violations.append(
                        f"Single-word directory '{name_full}': {path}"
                    )

            # Check generic prohibited names
            if path.is_file() and name_stem in PROHIBITED_GENERIC_NAMES:
                violations.append(f"Generic prohibited name '{path.name}': {path}")

            # Check single-word names
            if path.is_file():
                if name_full in DOCUMENTED_FILE_EXCEPTIONS:
                    continue
                # Python file check (snake_case with at least one underscore)
                if path.suffix == ".py" and "_" not in name_stem:
                    violations.append(f"Single-word Python file '{path.name}': {path}")
                # Frontend file check (kebab-case with at least one hyphen or PascalCase)
                elif path.suffix in {".ts", ".tsx"} and "-" not in name_stem:
                    has_word_boundary = any(char.isupper() for char in path.stem[1:])
                    if not has_word_boundary and not path.stem.isupper():
                        violations.append(f"Single-word frontend file '{path.name}': {path}")

    return violations


def main() -> int:
    root_dir = Path(__file__).resolve().parents[1]
    violations = check_naming(root_dir)

    if violations:
        print(f"Error: {len(violations)} naming convention violation(s) found:")
        for violation in violations:
            print(f"  - {violation}")
        print("\nAll folders and files must have descriptive, multi-word domain names.")
        return 1

    print("Success: All scanned files and directories satisfy descriptive naming standards.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
