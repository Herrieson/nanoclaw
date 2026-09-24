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
                "reason": 'Original same-group verifier could not be materialized as an executable workplace verifier. Validation reasons: turn_1:missing_score_output_marker; turn_1:syntax_error:unterminated string literal (detected at line 45):line_45; turn_2:missing_score_output_marker; turn_2:syntax_error:unterminated string literal (detected at line 44):line_44.',
            }
        ],
        "verifier_materialization": {
            "dataset": 'round_01_aligned_mix_800',
            "group": 'multi_turn_aligned',
            "source_task_id": 'data_1237',
            "imported_task_id": 'data_round_01_aligned_mix_800_0091',
            "action": 'conservative_fallback_raw_syntax_bad',
        },
    }
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
