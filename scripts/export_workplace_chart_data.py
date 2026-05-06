from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any
from xml.sax.saxutils import escape
import zipfile

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from nanoclaw.evaluation_visualization import (  # noqa: E402
    _evaluated_objective_score,
    _row_is_infra_failure,
)


SUMMARY_FIELDS = (
    "total_runs",
    "completed_runs",
    "skipped_incomplete_runs",
    "skipped_infra_failure_runs",
    "evaluated_runs",
    "scored_runs",
    "perfect_score_runs",
    "perfect_score_rate",
    "evaluation_issue_runs",
    "run_success_rate",
    "workplace_scored_runs",
    "trace_scored_runs",
    "average_workplace_score",
    "average_trace_score",
    "average_objective_score",
    "benchmark_score",
)


@dataclass(frozen=True, slots=True)
class ChartEntry:
    label: str
    summary_path: Path
    runner: str
    dataset: str
    group: str
    model: str


@dataclass(frozen=True, slots=True)
class SheetSpec:
    name: str
    chart_title: str
    chart_kind: str
    entries: tuple[ChartEntry, ...]
    exclude_infra_failures: bool = False


@dataclass(frozen=True, slots=True)
class Sheet:
    name: str
    rows: list[list[Any]]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Export the data represented by workplace suite SVG charts into one XLSX workbook."
        )
    )
    parser.add_argument(
        "--eval-root",
        required=True,
        help="Evaluation root written by run_nanoclaw_workplace_suite.sh or run_docker_workplace_suite.sh.",
    )
    parser.add_argument(
        "--mode",
        choices=("nanoclaw", "docker"),
        required=True,
        help="Suite layout to inspect.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output .xlsx path.",
    )
    parser.add_argument(
        "--exclude-infra-failures",
        action="store_true",
        help="Also add sheets matching *_exclude_infra.svg charts.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    eval_root = _resolve_path(args.eval_root)
    if not eval_root.exists():
        raise SystemExit(f"Evaluation root does not exist: {eval_root}")

    if args.mode == "nanoclaw":
        specs = _build_nanoclaw_specs(eval_root)
    else:
        specs = _build_docker_specs(eval_root)

    expanded_specs: list[SheetSpec] = []
    for spec in specs:
        expanded_specs.append(spec)
        if args.exclude_infra_failures:
            expanded_specs.append(
                SheetSpec(
                    name=f"{spec.name}_exinfra",
                    chart_title=f"{spec.chart_title} (Exclude Infra Failures)",
                    chart_kind=spec.chart_kind,
                    entries=spec.entries,
                    exclude_infra_failures=True,
                )
            )

    sheet_pairs = [
        (spec, _build_data_sheet(spec))
        for spec in expanded_specs
        if spec.entries
    ]
    if not sheet_pairs:
        raise SystemExit(f"No chart summary data found under {eval_root}")

    data_sheets = _dedupe_sheet_names([sheet for _, sheet in sheet_pairs])
    index_sheet = _build_index_sheet(
        data_sheets,
        [spec for spec, _sheet in sheet_pairs],
    )
    output_path = _resolve_path(args.output)
    write_xlsx(output_path, [index_sheet, *data_sheets])
    print(f"Wrote chart data workbook to {output_path}")
    return 0


def _resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


def _build_nanoclaw_specs(eval_root: Path) -> list[SheetSpec]:
    specs: list[SheetSpec] = []
    suite_entries: list[ChartEntry] = []
    group_breakdown_entries: list[ChartEntry] = []

    for dataset_dir in _discover_dataset_dirs(eval_root):
        dataset = dataset_dir.name
        dataset_entries = _entries_for_model_summaries(
            sorted((dataset_dir / "merged").glob("*/evaluation_summary.json")),
            runner="",
            dataset=dataset,
            group="",
            label_prefix="",
        )
        if dataset_entries:
            specs.append(
                SheetSpec(
                    name=f"dataset_{dataset}",
                    chart_title=f"{dataset} model comparison",
                    chart_kind="dataset",
                    entries=tuple(dataset_entries),
                )
            )
            suite_entries.extend(
                _with_labels(
                    dataset_entries,
                    label_prefix=f"{dataset}__",
                )
            )

        group_root = dataset_dir / "_group_reports"
        if not group_root.is_dir():
            continue
        for group_dir in sorted(path for path in group_root.iterdir() if path.is_dir()):
            group = group_dir.name
            group_entries = _entries_for_model_summaries(
                sorted(group_dir.glob("*/evaluation_summary.json")),
                runner="",
                dataset=dataset,
                group=group,
                label_prefix="",
            )
            if group_entries:
                group_breakdown_entries.extend(
                    _with_labels(
                        group_entries,
                        label_prefix=f"{dataset}__{group}__",
                    )
                )
                specs.append(
                    SheetSpec(
                        name=f"{dataset}_{group}",
                        chart_title=f"{dataset} {group} model comparison",
                        chart_kind="group",
                        entries=tuple(group_entries),
                    )
                )

    if group_breakdown_entries:
        specs.insert(
            0,
            SheetSpec(
                name="group_breakdown",
                chart_title="Nanoclaw workplace evaluation: dataset x group x model",
                chart_kind="group_breakdown",
                entries=tuple(group_breakdown_entries),
            ),
        )
    if suite_entries:
        specs.insert(
            0,
            SheetSpec(
                name="suite",
                chart_title="Nanoclaw workplace evaluation: dataset x model",
                chart_kind="suite",
                entries=tuple(suite_entries),
            ),
        )
    return specs


def _build_docker_specs(eval_root: Path) -> list[SheetSpec]:
    specs: list[SheetSpec] = []
    combined_entries: list[ChartEntry] = []
    combined_group_breakdown_entries: list[ChartEntry] = []

    for runner_dir in _discover_runner_dirs(eval_root):
        runner = runner_dir.name
        runner_suite_entries: list[ChartEntry] = []
        runner_group_breakdown_entries: list[ChartEntry] = []
        runner_specs: list[SheetSpec] = []

        for dataset_dir in _discover_dataset_dirs(runner_dir):
            dataset = dataset_dir.name
            dataset_entries = _entries_for_model_summaries(
                sorted((dataset_dir / "merged").glob("*/evaluation_summary.json")),
                runner=runner,
                dataset=dataset,
                group="",
                label_prefix="",
            )
            if dataset_entries:
                runner_specs.append(
                    SheetSpec(
                        name=f"{runner}_{dataset}",
                        chart_title=f"{runner} {dataset} model comparison",
                        chart_kind="runner_dataset",
                        entries=tuple(dataset_entries),
                    )
                )
                runner_suite_entries.extend(
                    _with_labels(dataset_entries, label_prefix=f"{dataset}__")
                )
                combined_entries.extend(
                    _with_labels(dataset_entries, label_prefix=f"{runner}__{dataset}__")
                )

            group_root = dataset_dir / "_group_reports"
            if not group_root.is_dir():
                continue
            for group_dir in sorted(path for path in group_root.iterdir() if path.is_dir()):
                group = group_dir.name
                group_entries = _entries_for_model_summaries(
                    sorted(group_dir.glob("*/evaluation_summary.json")),
                    runner=runner,
                    dataset=dataset,
                    group=group,
                    label_prefix="",
                )
                if group_entries:
                    runner_group_breakdown_entries.extend(
                        _with_labels(
                            group_entries,
                            label_prefix=f"{dataset}__{group}__",
                        )
                    )
                    combined_group_breakdown_entries.extend(
                        _with_labels(
                            group_entries,
                            label_prefix=f"{runner}__{dataset}__{group}__",
                        )
                    )
                    runner_specs.append(
                        SheetSpec(
                            name=f"{runner}_{dataset}_{group}",
                            chart_title=f"{runner} {dataset} {group} model comparison",
                            chart_kind="runner_group",
                            entries=tuple(group_entries),
                        )
                    )

        if runner_suite_entries:
            specs.append(
                SheetSpec(
                    name=f"{runner}_suite",
                    chart_title=f"{runner} workplace evaluation: dataset x model",
                    chart_kind="runner_suite",
                    entries=tuple(runner_suite_entries),
                )
            )
        if runner_group_breakdown_entries:
            specs.append(
                SheetSpec(
                    name=f"{runner}_group_breakdown",
                    chart_title=f"{runner} workplace evaluation: dataset x group x model",
                    chart_kind="runner_group_breakdown",
                    entries=tuple(runner_group_breakdown_entries),
                )
            )
        specs.extend(runner_specs)

    if combined_entries:
        specs.insert(
            0,
            SheetSpec(
                name="docker_combined",
                chart_title="Docker workplace evaluation: runner x dataset x model",
                chart_kind="docker_combined",
                entries=tuple(combined_entries),
            ),
        )
    if combined_group_breakdown_entries:
        insert_index = 1 if combined_entries else 0
        specs.insert(
            insert_index,
            SheetSpec(
                name="docker_group_breakdown",
                chart_title="Docker workplace evaluation: runner x dataset x group x model",
                chart_kind="docker_group_breakdown",
                entries=tuple(combined_group_breakdown_entries),
            ),
        )
    return specs


def _discover_dataset_dirs(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.iterdir()
        if path.is_dir() and not path.name.startswith("_") and (path / "merged").is_dir()
    )


def _discover_runner_dirs(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.iterdir()
        if path.is_dir() and not path.name.startswith("_") and _discover_dataset_dirs(path)
    )


def _entries_for_model_summaries(
    summary_paths: list[Path],
    *,
    runner: str,
    dataset: str,
    group: str,
    label_prefix: str,
) -> list[ChartEntry]:
    entries: list[ChartEntry] = []
    for summary_path in summary_paths:
        model = summary_path.parent.name
        entries.append(
            ChartEntry(
                label=f"{label_prefix}{model}",
                summary_path=summary_path.resolve(),
                runner=runner,
                dataset=dataset,
                group=group,
                model=model,
            )
        )
    return entries


def _with_labels(entries: list[ChartEntry], *, label_prefix: str) -> list[ChartEntry]:
    return [
        ChartEntry(
            label=f"{label_prefix}{entry.model}",
            summary_path=entry.summary_path,
            runner=entry.runner,
            dataset=entry.dataset,
            group=entry.group,
            model=entry.model,
        )
        for entry in entries
    ]


def _build_data_sheet(spec: SheetSpec) -> Sheet:
    rows: list[dict[str, Any]] = []
    for entry in spec.entries:
        summary = json.loads(entry.summary_path.read_text(encoding="utf-8"))
        chart_metrics = _load_chart_metrics(
            entry.summary_path,
            summary=summary,
            exclude_infra_failures=spec.exclude_infra_failures,
        )
        row = {
            "chart_label": entry.label,
            "runner": entry.runner,
            "dataset": entry.dataset,
            "group": entry.group,
            "model": entry.model,
            "chart_kind": spec.chart_kind,
            "infra_failures_excluded": spec.exclude_infra_failures,
            "chart_total_runs": chart_metrics["total_runs"],
            "chart_scored_runs": chart_metrics["scored_runs"],
            "chart_perfect_score_runs": chart_metrics["perfect_score_runs"],
            "perfect_score_rate": chart_metrics["perfect_score_rate"],
            "average_objective_score": chart_metrics["average_objective_score"],
            "summary_path": _repo_relative(entry.summary_path),
            "evaluation_path": _repo_relative(entry.summary_path.parent / "evaluation.json"),
        }
        for field in SUMMARY_FIELDS:
            row[f"summary_{field}"] = summary.get(field)
        rows.append(row)

    rows.sort(
        key=lambda item: (
            -float(item["average_objective_score"]),
            str(item["chart_label"]).lower(),
        )
    )

    headers = [
        "rank",
        "chart_label",
        "runner",
        "dataset",
        "group",
        "model",
        "chart_kind",
        "infra_failures_excluded",
        "chart_total_runs",
        "chart_scored_runs",
        "chart_perfect_score_runs",
        "perfect_score_rate",
        "average_objective_score",
        *[f"summary_{field}" for field in SUMMARY_FIELDS],
        "summary_path",
        "evaluation_path",
    ]

    data_rows: list[list[Any]] = [
        [f"chart_title: {spec.chart_title}"],
        headers,
    ]
    for rank, row in enumerate(rows, start=1):
        data_rows.append([rank, *[row.get(header) for header in headers[1:]]])
    return Sheet(name=spec.name, rows=data_rows)


def _load_chart_metrics(
    summary_path: Path,
    *,
    summary: dict[str, Any],
    exclude_infra_failures: bool,
) -> dict[str, int | float]:
    if not exclude_infra_failures:
        total_runs = _int_value(summary.get("total_runs"))
        scored_runs = _int_value(summary.get("scored_runs"))
        perfect_score_runs = _int_value(summary.get("perfect_score_runs"))
        return {
            "total_runs": total_runs,
            "scored_runs": scored_runs,
            "perfect_score_runs": perfect_score_runs,
            "perfect_score_rate": _float_value(summary.get("perfect_score_rate")),
            "average_objective_score": _float_value(summary.get("average_objective_score")),
        }

    evaluation_path = summary_path.parent / "evaluation.json"
    payload = json.loads(evaluation_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{evaluation_path} does not contain a JSON array")

    total_runs = 0
    scored_runs = 0
    perfect_score_runs = 0
    scored_values: list[float] = []
    for item in payload:
        if not isinstance(item, dict) or _row_is_infra_failure(item):
            continue
        total_runs += 1
        score = _evaluated_objective_score(item)
        if score is None:
            continue
        scored_runs += 1
        scored_values.append(score)
        if score == 100.0:
            perfect_score_runs += 1
    return {
        "total_runs": total_runs,
        "scored_runs": scored_runs,
        "perfect_score_runs": perfect_score_runs,
        "perfect_score_rate": round((perfect_score_runs / total_runs) * 100, 2)
        if total_runs
        else 0.0,
        "average_objective_score": round(sum(scored_values) / len(scored_values), 2)
        if scored_values
        else 0.0,
    }


def _int_value(value: Any) -> int:
    return int(value) if isinstance(value, (int, float)) else 0


def _float_value(value: Any) -> float:
    return float(value) if isinstance(value, (int, float)) else 0.0


def _build_index_sheet(data_sheets: list[Sheet], specs: list[SheetSpec]) -> Sheet:
    rows: list[list[Any]] = [
        ["sheet", "chart_title", "chart_kind", "infra_failures_excluded", "rows"],
    ]
    for sheet, spec in zip(data_sheets, specs, strict=True):
        rows.append(
            [
                sheet.name,
                spec.chart_title,
                spec.chart_kind,
                spec.exclude_infra_failures,
                max(0, len(sheet.rows) - 2),
            ]
        )
    return Sheet(name="index", rows=rows)


def write_xlsx(output_path: Path, sheets: list[Sheet]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    unique_sheets = _dedupe_sheet_names(sheets)

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", _content_types_xml(len(unique_sheets)))
        archive.writestr("_rels/.rels", _root_rels_xml())
        archive.writestr("xl/workbook.xml", _workbook_xml(unique_sheets))
        archive.writestr("xl/_rels/workbook.xml.rels", _workbook_rels_xml(len(unique_sheets)))
        for index, sheet in enumerate(unique_sheets, start=1):
            archive.writestr(f"xl/worksheets/sheet{index}.xml", _worksheet_xml(sheet.rows))


def _dedupe_sheet_names(sheets: list[Sheet]) -> list[Sheet]:
    used: set[str] = set()
    output: list[Sheet] = []
    for sheet in sheets:
        base = _safe_sheet_name(sheet.name)
        name = base
        suffix = 2
        while name.lower() in used:
            tail = f"_{suffix}"
            name = f"{base[:31 - len(tail)]}{tail}"
            suffix += 1
        used.add(name.lower())
        output.append(Sheet(name=name, rows=sheet.rows))
    return output


def _safe_sheet_name(value: str) -> str:
    replacements = {
        "round_01_aligned_mix_subset_100": "r01_subset100",
        "round_01_aligned_mix_subset_20": "r01_subset20",
        "round_01_aligned_mix_800": "r01_mix800",
        "persona_aligned_mix_subset_100": "persona_subset100",
        "persona_aligned_mix_subset_20": "persona_subset20",
        "persona_aligned_mix_200": "persona_mix200",
        "multi_turn_aligned": "multi_turn",
        "skills_aligned": "skills",
        "hard_aligned": "hard",
        "docker_combined": "docker_combined",
        "dataset_": "ds_",
        "_exinfra": "_noinfra",
    }
    normalized = value
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)
    normalized = re.sub(r"[\[\]:*?/\\]", "_", normalized)
    normalized = re.sub(r"[^A-Za-z0-9_ -]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip(" _")
    if not normalized:
        normalized = "sheet"
    return normalized[:31]


def _content_types_xml(sheet_count: int) -> str:
    overrides = [
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
    ]
    for index in range(1, sheet_count + 1):
        overrides.append(
            f'<Override PartName="/xl/worksheets/sheet{index}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        f"{''.join(overrides)}"
        "</Types>\n"
    )


def _root_rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        "</Relationships>\n"
    )


def _workbook_xml(sheets: list[Sheet]) -> str:
    sheet_items = []
    for index, sheet in enumerate(sheets, start=1):
        sheet_items.append(
            f'<sheet name="{escape(sheet.name)}" sheetId="{index}" r:id="rId{index}"/>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<sheets>{''.join(sheet_items)}</sheets>"
        "</workbook>\n"
    )


def _workbook_rels_xml(sheet_count: int) -> str:
    relationships = []
    for index in range(1, sheet_count + 1):
        relationships.append(
            f'<Relationship Id="rId{index}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{index}.xml"/>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f"{''.join(relationships)}"
        "</Relationships>\n"
    )


def _worksheet_xml(rows: list[list[Any]]) -> str:
    row_items = []
    for row_number, values in enumerate(rows, start=1):
        cells = []
        for column_index, value in enumerate(values, start=1):
            cells.append(_cell_xml(_cell_reference(row_number, column_index), value))
        row_items.append(f'<row r="{row_number}">{"".join(cells)}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"<sheetData>{''.join(row_items)}</sheetData>"
        "</worksheet>\n"
    )


def _cell_xml(reference: str, value: Any) -> str:
    if value is None:
        return f'<c r="{reference}"/>'
    if isinstance(value, bool):
        return f'<c r="{reference}" t="b"><v>{1 if value else 0}</v></c>'
    if isinstance(value, (int, float)):
        return f'<c r="{reference}"><v>{value}</v></c>'
    text = _clean_xml_text(str(value))
    return f'<c r="{reference}" t="inlineStr"><is><t>{escape(text)}</t></is></c>'


def _cell_reference(row_number: int, column_index: int) -> str:
    letters = ""
    index = column_index
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return f"{letters}{row_number}"


def _clean_xml_text(value: str) -> str:
    return re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", value)


def _repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
