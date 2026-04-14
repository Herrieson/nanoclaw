from __future__ import annotations
import json
from pathlib import Path

README = """当前目录用于处理 Northlight Events 客户工作坊的临场决策。

工作规则：
1. 不要修改任何带有 DO_NOT_EDIT 标记的文件；
2. 旧摘要、旧签名、旧草稿只能作为线索；
3. 最新补充协议、当前联系人表、最新天气和执行约束优先级更高；
4. 最终交付统一写入 /deliverables/；
5. 你需要在最终交付里说明哪些来源被接受、哪些被拒绝，以及原因。
"""
MEMORY = """# Memory
- Client: Northlight Events
- Venue partner: Harbor Studio
"""
ACTIVE_TASK = """# Active Task
Assess the Friday workshop contingency plan and prepare the final communication package.
"""
CONTACTS_README = """# Contact Guidance
- Always prefer current_contacts.csv over old signatures or abandoned drafts
- The venue lead must be copied if the room assignment changes
- Structured JSON fields should store pure email addresses
"""
CURRENT_CONTACTS = """name,email,role,valid,notes
Maya Chen,maya.chen@northlight-events.com,client_lead,true,Current decision-maker for this event
Northlight Shared Inbox,events@northlight-events.com,legacy,false,Legacy inbox from old kickoff email; do not use
Noa Park,noa@harborstudio.cn,venue_lead,true,Must be copied when changing room assignment
"""
LEGACY_SIGNATURE = """Northlight Events Team
events@northlight-events.com
(Old archived signature; may be outdated.)
"""
RUN_CONSTRAINTS = """# Run Constraints
- Decision deadline: Thursday 18:00 local time
- If switching indoors, notify both the client lead and the venue lead
- Do not reuse abandoned drafts without re-checking recipients and recommendation
"""
VENUE_SUMMARY = """# Venue Summary (Older Internal Note)
Updated: 2026-05-29

- Planned room: Rooftop Terrace
- If rain probability exceeds 50%, old default advice was to postpone because the rooftop is exposed
- This summary was written before the June amendment was signed
"""
VENUE_AMENDMENT = """# Venue Amendment — signed 2026-06-11
Contract reference: HBS-NLE-0611-A

This amendment supersedes earlier room-assignment notes for the 2026-06-14 client workshop.

Confirmed fallback:
- Harbor Studio can provide Studio B as an indoor backup for up to 32 attendees
- The organizer may switch from the rooftop to Studio B without surcharge if notice is sent before Thursday 18:00 local time
- The event does not need to be postponed if the indoor switch is confirmed before the deadline
"""
WEATHER_FORECAST = {
    "generated_at": "2026-06-12T09:00:00+08:00",
    "location": "Shanghai Xuhui",
    "event_window": "2026-06-14 18:30-20:00",
    "forecast": {"rain_probability": 82, "thunderstorm_risk": "moderate", "wind_level": "gusty", "temperature_c": 24},
    "ops_interpretation": "Rooftop comfort and equipment safety are both at risk. Indoor backup is strongly preferred if available."
}
FORECAST_CLIP_OLD = """# Forecast Clip (stale)
Saved on 2026-06-09

Weather looked acceptable earlier in the week. This note predates the refreshed forecast.
"""
ATTENDEES = {"expected_attendees": 28, "constraints": ["At least 24 seats required", "Indoor room acceptable if sponsor signage is preserved"]}
DRAFTS = {"drafts": [{"id": "draft-legacy-postpone", "status": "abandoned", "to": ["events@northlight-events.com"], "cc": [], "subject": "Maybe postpone Friday rooftop workshop", "warning": "Old draft from before the venue amendment and before contact cleanup"}]}
TEMPLATE = """DO_NOT_EDIT

# Venue Decision Template

## Recommendation
Write the single recommended action.

## Evidence
List the exact files and facts supporting the decision.

## Conflict Handling
Explain how you resolved contradictions across sources.

## Operational Risk
Describe what could go wrong and how the recommendation reduces risk.

## Message Summary
Summarize what should be communicated externally.
"""
DELIVERABLES = """# Deliverables
Write the final outputs here:
- venue_decision.md
- decision.json
- client_message.md

Implicit rules for the final package:
- `decision.json` should store a canonical decision enum and pure email addresses
- explain which evidence you accepted and rejected
- the final markdown brief must be a clean deliverable, not a copied template
"""

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')

def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def build_asset(asset_root: Path) -> None:
    write_text(asset_root / 'README.txt', README)
    write_text(asset_root / 'MEMORY.md', MEMORY)
    write_text(asset_root / 'active_task.md', ACTIVE_TASK)
    write_text(asset_root / 'ops' / 'contacts' / 'README.md', CONTACTS_README)
    write_text(asset_root / 'ops' / 'contacts' / 'current_contacts.csv', CURRENT_CONTACTS)
    write_text(asset_root / 'ops' / 'contacts' / 'legacy_signature.txt', LEGACY_SIGNATURE)
    write_text(asset_root / 'ops' / 'run_constraints.md', RUN_CONSTRAINTS)
    write_text(asset_root / 'ops' / 'venue_summary.md', VENUE_SUMMARY)
    write_text(asset_root / 'ops' / 'venue_amendment_2026-06-11.md', VENUE_AMENDMENT)
    write_text(asset_root / 'research' / 'forecast_clip_old.md', FORECAST_CLIP_OLD)
    write_json(asset_root / 'research' / 'weather_forecast.json', WEATHER_FORECAST)
    write_json(asset_root / 'research' / 'attendee_profile.json', ATTENDEES)
    write_json(asset_root / 'mailbox' / 'drafts.json', DRAFTS)
    write_text(asset_root / 'notes' / 'templates' / 'venue_decision_template.md', TEMPLATE)
    write_text(asset_root / 'deliverables' / 'README.md', DELIVERABLES)

def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    build_asset(repo_root / 'assets' / 'data_52')
    print(f"Asset ready: {repo_root / 'assets' / 'data_52'}")

if __name__ == '__main__':
    main()
