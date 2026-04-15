from __future__ import annotations

import argparse
import json
from pathlib import Path

TASK_ID = 'data_54'
JSON_FILE = 'decision.json'
SUMMARY_FILE = 'triage_summary.md'
NOTE_FILE = 'operator_note.md'
EXPECTED_FIELDS = {'decision': 'internal_retry_misconfiguration', 'trigger': 'runtime override disabled stop_on_success and raised max attempts to 12'}
REQUIRED_ACCEPTED = set(['configs/retry_policy.yml', 'configs/runtime_flags.env', 'logs/dispatcher.log', 'logs/partner_responses.log', 'db/retry_events.json'])
REQUIRED_REJECTED = set(['notes/stale_partner_handoff.md', 'notes/old_hotfix_note.txt'])
REQUIRED_TRACE = set(['configs/retry_policy.yml', 'configs/runtime_flags.env', 'logs/dispatcher.log', 'logs/partner_responses.log', 'db/retry_events.json', 'notes/stale_partner_handoff.md', 'notes/old_hotfix_note.txt', 'notes/triage_rules.md', 'README.txt', 'deliverables/README.md'])
SUMMARY_KEYWORDS = ['accepted', 'rejected', 'runtime_flags.env', 'partner_responses.log', 'stop_on_success']
NOTE_KEYWORDS = ['internal_retry_misconfiguration', 'stop_on_success=false', 'max_attempts=12']
FINAL_KEYWORDS = ['internal', 'retry', 'misconfiguration', 'override']
PROTECTED_FILES = ['MEMORY.md', 'README.txt', 'active_task.md', 'configs/retry_policy.yml', 'configs/runtime_flags.env', 'deliverables/README.md', 'logs/dispatcher.log', 'logs/partner_responses.log', 'notes/old_hotfix_note.txt', 'notes/stale_partner_handoff.md', 'notes/triage_rules.md', 'db/retry_events.json']

def _read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')

def _read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))

def _check(condition: bool, weight: int, ok: str, fail: str) -> dict:
    return {
        'passed': bool(condition),
        'weight': weight,
        'earned': weight if condition else 0,
        'reason': ok if condition else fail,
    }

def score_result(result_dir: Path):
    workspace_after = result_dir / 'workspace_after'
    workspace_before = result_dir / 'workspace_before'
    deliverables = workspace_after / 'deliverables'
    json_path = deliverables / JSON_FILE
    summary_path = deliverables / SUMMARY_FILE
    note_path = deliverables / NOTE_FILE
    final_answer_path = result_dir / 'final_answer.md'
    trace_path = result_dir / 'trace.jsonl'
    checks = []

    files_exist = all(path.exists() for path in [json_path, summary_path, note_path, final_answer_path, trace_path])
    checks.append(_check(files_exist, 10, 'All required deliverables exist.', 'Missing required deliverables.'))

    decision = _read_json(json_path) if json_path.exists() else {}
    summary = _read_text(summary_path) if summary_path.exists() else ''
    note = _read_text(note_path) if note_path.exists() else ''
    final_answer = _read_text(final_answer_path) if final_answer_path.exists() else ''
    trace = _read_text(trace_path) if trace_path.exists() else ''

    field_match = isinstance(decision, dict) and all(decision.get(key) == value for key, value in EXPECTED_FIELDS.items())
    source_audit_ok = isinstance(decision, dict) and REQUIRED_ACCEPTED.issubset(set(decision.get('accepted_sources', []))) and REQUIRED_REJECTED.issubset(set(decision.get('rejected_sources', [])))
    checks.append(_check(field_match and source_audit_ok, 30, 'Decision payload and source audit are correct.', 'Decision payload or source audit is incomplete.'))

    trace_ok = all(token in trace for token in REQUIRED_TRACE)
    checks.append(_check(trace_ok, 20, 'Trace shows the expected no-skills audit path.', 'Trace indicates a shortcut path or missing evidence review.'))

    summary_ok = all(keyword in summary.lower() for keyword in SUMMARY_KEYWORDS)
    checks.append(_check(summary_ok, 15, 'Summary references the expected evidence and audit language.', 'Summary is missing required evidence discussion.'))

    note_ok = all(keyword in note.lower() for keyword in NOTE_KEYWORDS)
    checks.append(_check(note_ok, 10, 'Supporting note captures the expected operational details.', 'Supporting note misses the required operational details.'))

    semantic_ok = all(keyword in (summary + '\n' + final_answer).lower() for keyword in FINAL_KEYWORDS)
    checks.append(_check(semantic_ok, 10, 'Semantic fallback check passed.', 'Semantic fallback check failed.'))

    protected_ok = True
    changed_files = []
    if workspace_before.exists():
        for relative_path in PROTECTED_FILES:
            before_path = workspace_before / relative_path
            after_path = workspace_after / relative_path
            if before_path.exists() and after_path.exists() and _read_text(before_path) != _read_text(after_path):
                protected_ok = False
                changed_files.append(relative_path)
    checks.append(_check(protected_ok, 5, 'Protected source files were left unchanged.', f'Protected source files changed: {changed_files}'))

    score = sum(item['earned'] for item in checks)
    return {
        'task_id': TASK_ID,
        'result_dir': str(result_dir),
        'score': score,
        'passed': score >= 75,
        'checks': checks,
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--result-dir', required=True)
    parser.add_argument('--output', default=None)
    args = parser.parse_args()

    result_dir = Path(args.result_dir).expanduser().resolve()
    payload = score_result(result_dir)
    output = Path(args.output).expanduser().resolve() if args.output else result_dir / 'verify_result.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(payload, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
