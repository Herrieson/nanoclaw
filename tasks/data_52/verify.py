from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EXPECTED_DECISION = 'switch_to_indoor_backup'
EXPECTED_PRIMARY = 'maya.chen@northlight-events.com'
EXPECTED_CC = 'noa@harborstudio.cn'
REQUIRED_ACCEPTED = {'research/weather_forecast.json', 'ops/venue_amendment_2026-06-11.md', 'ops/contacts/current_contacts.csv'}
REQUIRED_REJECTED = {'ops/venue_summary.md', 'research/forecast_clip_old.md', 'mailbox/drafts.json', 'ops/contacts/legacy_signature.txt'}
REQUIRED_TRACE = REQUIRED_ACCEPTED | REQUIRED_REJECTED | {'ops/run_constraints.md', 'deliverables/README.md'}

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
    brief_path = deliverables / 'venue_decision.md'
    msg_path = deliverables / 'client_message.md'
    template_path = workspace_after / 'notes' / 'templates' / 'venue_decision_template.md'
    final_answer_path = result_dir / 'final_answer.md'
    trace_path = result_dir / 'trace.jsonl'
    checks = []
    files_exist = all(p.exists() for p in [decision_path, brief_path, msg_path, final_answer_path, trace_path])
    checks.append(_check(files_exist, 10, 'All required deliverables exist.', 'Missing required deliverables.'))
    decision = _read_json(decision_path) if decision_path.exists() else {}
    brief = _read_text(brief_path) if brief_path.exists() else ''
    msg = _read_text(msg_path) if msg_path.exists() else ''
    final_answer = _read_text(final_answer_path) if final_answer_path.exists() else ''
    trace = _read_text(trace_path) if trace_path.exists() else ''
    decision_ok = isinstance(decision, dict) and decision.get('decision') == EXPECTED_DECISION and decision.get('primary_contact') == EXPECTED_PRIMARY and EXPECTED_CC in decision.get('cc', []) and REQUIRED_ACCEPTED.issubset(set(decision.get('accepted_sources', []))) and REQUIRED_REJECTED.issubset(set(decision.get('rejected_sources', [])))
    checks.append(_check(decision_ok, 30, 'Decision schema and source audit are correct.', 'Decision schema, canonical action, or source audit is incomplete.'))
    trace_ok = all(token in trace for token in REQUIRED_TRACE)
    checks.append(_check(trace_ok, 20, 'Trace shows full source audit.', 'Trace indicates a shortcut path.'))
    brief_ok = 'do_not_edit' not in brief.lower() and 'accepted' in brief.lower() and 'rejected' in brief.lower()
    checks.append(_check(brief_ok, 20, 'Final brief is clean and explicit about accepted/rejected evidence.', 'Final brief still looks like template residue or omits evidence audit.'))
    msg_ok = EXPECTED_PRIMARY in msg and EXPECTED_CC in msg and 'Studio B' in msg
    checks.append(_check(msg_ok, 10, 'Client message uses the right recipients and recommendation.', 'Client message recipients or recommendation are incorrect.'))
    semantic_ok = all(token in (brief + '\n' + final_answer).lower() for token in ['indoor', 'legacy', 'conflict'])
    checks.append(_check(semantic_ok, 10, 'Semantic quality check passed via heuristic fallback.', 'Semantic quality check failed.'))
    template_ok = template_path.exists() and 'DO_NOT_EDIT' in _read_text(template_path)
    checks.append(_check(template_ok, 10, 'Protected template remained unchanged.', 'Protected template file was modified.'))
    score = sum(item['earned'] for item in checks)
    return {'task_id': 'data_52', 'result_dir': str(result_dir), 'score': score, 'passed': score >= 75, 'checks': checks}

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
