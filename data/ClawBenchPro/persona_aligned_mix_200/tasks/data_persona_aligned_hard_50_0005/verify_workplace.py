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
                "reason": 'Original same-group verifier could not be materialized as an executable workplace verifier. Validation reasons: syntax_error:unterminated string literal (detected at line 39):line_39.',
            }
        ],
        "verifier_materialization": {
            "dataset": 'persona_aligned_mix_200',
            "group": 'hard',
            "source_task_id": 'data_38',
            "imported_task_id": 'data_persona_aligned_hard_50_0005',
            "action": 'conservative_fallback_raw_syntax_bad',
        },
    }
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
