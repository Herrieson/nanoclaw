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
                "reason": 'Original same-group verifier could not be materialized as an executable workplace verifier. Validation reasons: turn_1:empty; turn_1:missing_score_output_marker; turn_2:empty; turn_2:missing_score_output_marker; turn_3:empty; turn_3:missing_score_output_marker.',
            }
        ],
        "verifier_materialization": {
            "dataset": 'persona_aligned_mix_200',
            "group": 'multi_turn',
            "source_task_id": 'data_06',
            "imported_task_id": 'data_persona_aligned_multi_turn_50_0003',
            "action": 'conservative_fallback_raw_empty',
        },
    }
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
