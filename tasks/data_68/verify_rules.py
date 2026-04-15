from __future__ import annotations
import argparse
import json
from pathlib import Path

EXPECTED = {'decision': 'uv_commute_layers', 'trigger': 'current comments and saves both favor 通勤防晒叠穿', 'accepted_sources': ['research/comment_clusters.json', 'research/post_performance.csv', 'notes/current_merch_window.md'], 'rejected_sources': ['notes/stale_keyword_memo.md']}
REQUIRED_TRACE = ['README.txt', 'deliverables/README.md', 'notes/triage_rules.md', 'research/comment_clusters.json', 'research/post_performance.csv', 'notes/current_merch_window.md', 'notes/stale_keyword_memo.md']
SUMMARY_TOKENS = ['accepted', 'rejected', 'comment_clusters', 'post_performance', 'stale_keyword_memo']
NOTE_TOKENS = ['uv_commute_layers', '通勤防晒']
SEMANTIC_TOKENS = ['通勤', '防晒', '旧 memo', '评论']
DELIVERABLE_FILES = ['topic_recommendation.md', 'decision.json', 'editor_note.md']
TASK_ID = "data_68"
SUMMARY_FILE = DELIVERABLE_FILES[0]
NOTE_FILE = DELIVERABLE_FILES[2]


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _check(cond: bool, weight: int, ok: str, fail: str) -> dict:
    return {
        "passed": bool(cond),
        "weight": weight,
        "earned": weight if cond else 0,
        "reason": ok if cond else fail,
    }


def _matches_expectations(decision: dict, expected: dict) -> bool:
    if not isinstance(decision, dict):
        return False
    for key, expected_value in expected.items():
        actual_value = decision.get(key)
        if isinstance(expected_value, list):
            if not isinstance(actual_value, list):
                return False
            if set(actual_value) != set(expected_value):
                return False
        else:
            if actual_value != expected_value:
                return False
    return True


def score_result(result_dir: Path):
    workspace_after = result_dir / "workspace_after"
    deliverables = workspace_after / "deliverables"
    decision_path = deliverables / "decision.json"
    summary_path = deliverables / SUMMARY_FILE
    note_path = deliverables / NOTE_FILE
    final_answer_path = result_dir / "final_answer.md"
    trace_path = result_dir / "trace.jsonl"

    checks = []
    required_files = [decision_path, summary_path, note_path, final_answer_path, trace_path]
    files_exist = all(path.exists() for path in required_files)
    checks.append(_check(files_exist, 10, "All required deliverables exist.", "Missing required deliverables."))

    decision = _read_json(decision_path) if decision_path.exists() else {}
    summary = _read_text(summary_path).lower() if summary_path.exists() else ""
    note = _read_text(note_path).lower() if note_path.exists() else ""
    final_answer = _read_text(final_answer_path).lower() if final_answer_path.exists() else ""
    trace = _read_text(trace_path) if trace_path.exists() else ""

    decision_ok = _matches_expectations(decision, EXPECTED)
    checks.append(_check(decision_ok, 30, "Decision schema and evidence audit are correct.", "Decision payload is incomplete or incorrect."))

    trace_ok = all(token in trace for token in REQUIRED_TRACE)
    checks.append(_check(trace_ok, 20, "Trace shows the expected audit path.", "Trace suggests the agent skipped key evidence."))

    summary_ok = all(token in summary for token in SUMMARY_TOKENS)
    checks.append(_check(summary_ok, 20, "Summary explains accepted and rejected evidence.", "Summary omits required evidence audit details."))

    note_ok = all(token in note for token in NOTE_TOKENS)
    checks.append(_check(note_ok, 10, "Operational note captures the key action.", "Operational note misses required action details."))

    semantic_ok = all(token in (summary + "\n" + final_answer) for token in SEMANTIC_TOKENS)
    checks.append(_check(semantic_ok, 10, "Semantic heuristic passed.", "Semantic heuristic failed."))

    score = sum(item["earned"] for item in checks)
    return {
        "task_id": TASK_ID,
        "result_dir": str(result_dir),
        "score": score,
        "passed": score >= 75,
        "checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    result_dir = Path(args.result_dir).expanduser().resolve()
    payload = score_result(result_dir)
    output = Path(args.output).expanduser().resolve() if args.output else result_dir / "verify_result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
