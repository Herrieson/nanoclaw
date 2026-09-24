from __future__ import annotations

import json
import os
import sys


def main() -> None:
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = {
        "total_score": 0,
        "details": [
            {
                "item": "verifier_materialization_fallback",
                "score": 0,
                "max_score": 100,
                "passed": False,
                "reason": 'This multi-turn task is evaluated from the original per-turn verifier scripts stored in verifiers/*.jsonl. The task-local verify_workplace.py is intentionally a non-authoritative zero-score fallback.',
            }
        ],
        "verifier_materialization": {
            "dataset": 'persona_aligned_mix_200',
            "group": 'multi_turn',
            "source_task_id": 'data_94',
            "imported_task_id": 'data_persona_aligned_multi_turn_50_0001',
            "action": 'task_local_turn_verifier_placeholder',
        },
    }
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
