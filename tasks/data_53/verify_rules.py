from __future__ import annotations
import argparse, json
from pathlib import Path

EXPECTED_DECISION = 'internal_misconfiguration'
EXPECTED_TRIGGER = 'scheduled reset replay ran with dry_run=false'
REQUIRED_ACCEPTED = {'logs/api_gateway.log', 'logs/worker.log', 'configs/cron_jobs.txt', 'db/reset_requests.json'}
REQUIRED_REJECTED = {'notes/handoff_old.md', 'notes/legacy_command_snippet.txt'}
REQUIRED_TRACE = REQUIRED_ACCEPTED | REQUIRED_REJECTED | {'notes/triage_rules.md', 'configs/alerts.ini', 'README.txt', 'deliverables/README.md'}

def _read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))

def _read_text(path):
    return path.read_text(encoding='utf-8')

def _check(cond, weight, ok, fail):
    return {'passed': bool(cond), 'weight': weight, 'earned': weight if cond else 0, 'reason': ok if cond else fail}

def score_result(result_dir: Path):
    workspace_after = result_dir / 'workspace_after'
    deliverables = workspace_after / 'deliverables'
    decision_path = deliverables / 'decision.json'
    summary_path = deliverables / 'incident_summary.md'
    note_path = deliverables / 'operator_note.md'
    final_answer_path = result_dir / 'final_answer.md'
    trace_path = result_dir / 'trace.jsonl'
    checks = []
    files_exist = all(p.exists() for p in [decision_path, summary_path, note_path, final_answer_path, trace_path])
    checks.append(_check(files_exist, 10, 'All required deliverables exist.', 'Missing required deliverables.'))
    decision = _read_json(decision_path) if decision_path.exists() else {}
    summary = _read_text(summary_path) if summary_path.exists() else ''
    note = _read_text(note_path) if note_path.exists() else ''
    final_answer = _read_text(final_answer_path) if final_answer_path.exists() else ''
    trace = _read_text(trace_path) if trace_path.exists() else ''
    decision_ok = isinstance(decision, dict) and decision.get('decision') == EXPECTED_DECISION and decision.get('trigger') == EXPECTED_TRIGGER and REQUIRED_ACCEPTED.issubset(set(decision.get('accepted_sources', []))) and REQUIRED_REJECTED.issubset(set(decision.get('rejected_sources', [])))
    checks.append(_check(decision_ok, 30, 'Decision schema and source audit are correct.', 'Decision schema, trigger, or source audit is incomplete.'))
    trace_ok = all(token in trace for token in REQUIRED_TRACE)
    checks.append(_check(trace_ok, 20, 'Trace shows full no-skills audit.', 'Trace indicates a shortcut path.'))
    summary_ok = all(token in summary.lower() for token in ['accepted', 'rejected', 'worker.log', 'cron_jobs.txt', 'handoff_old.md'])
    checks.append(_check(summary_ok, 20, 'Incident summary is clean and explicit about accepted/rejected evidence.', 'Incident summary omits required evidence audit.'))
    note_ok = 'dry_run=false' in note and 'internal_misconfiguration' in note
    checks.append(_check(note_ok, 10, 'Operator note captures the trigger and classification.', 'Operator note does not clearly capture the trigger and classification.'))
    semantic_ok = all(token in (summary + '\n' + final_answer).lower() for token in ['internal', 'misconfiguration', 'legacy', 'worker'])
    checks.append(_check(semantic_ok, 10, 'Semantic quality check passed via heuristic fallback.', 'Semantic quality check failed.'))
    score = sum(item['earned'] for item in checks)
    return {'task_id': 'data_53', 'result_dir': str(result_dir), 'score': score, 'passed': score >= 75, 'checks': checks}

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
