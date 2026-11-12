import argparse
import asyncio
import json
from pathlib import Path
from diagnostics.workday_diagnostic_inspector import inspect_workday_target
from diagnostics.workday_diagnostic_models import TargetDiagnosticResult
from diagnostics.workday_diagnostic_reporter import (
    format_summary_table,
    format_target_report,
)
from scout.ats_adapters.workday_adapter.workday_cxs_client import (
    WorkdayCxsClient,
)

TARGETS_PATH = (
    Path(__file__).resolve().parents[1]
    / "registry"
    / "workday-investigation-targets.json"
)


async def run_diagnostics(
    employer_id: str | None = None,
    sample_limit: int = 3,
) -> list[TargetDiagnosticResult]:
    with open(TARGETS_PATH) as f:
        data = json.load(f)
    targets = data.get("targets", [])
    if employer_id:
        targets = [t for t in targets if t.get("employer_id") == employer_id]
        if not targets:
            raise ValueError(f"Target '{employer_id}' not found in registry.")

    results: list[TargetDiagnosticResult] = []
    client = WorkdayCxsClient()
    try:
        for index, target in enumerate(targets, start=1):
            name = target.get("name", "Unknown")
            print(f"[{index}/{len(targets)}] Inspecting {name}...")
            res = await inspect_workday_target(
                client, target, sample_limit=sample_limit
            )
            results.append(res)
    finally:
        await client.close()
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Workday ATS Diagnostic Tool")
    parser.add_argument("--target", help="Specific employer_id to diagnose")
    parser.add_argument(
        "--samples", type=int, default=3, help="Detail samples per employer"
    )
    parser.add_argument("--output", help="Path to write report output")
    args = parser.parse_args()

    results = asyncio.run(
        run_diagnostics(employer_id=args.target, sample_limit=args.samples)
    )
    report_text = (
        "\n"
        + "=" * 60
        + "\nWORKDAY ATS EXTRACTION DIAGNOSTIC REPORT\n"
        + "=" * 60
        + "\n\n"
    )
    for r in results:
        report_text += format_target_report(r) + "\n\n" + "-" * 40 + "\n\n"
    report_text += "\nSUMMARY TABLE\n\n" + format_summary_table(results) + "\n"
    print(report_text)
    if args.output:
        Path(args.output).write_text(report_text, encoding="utf-8")


if __name__ == "__main__":
    main()
