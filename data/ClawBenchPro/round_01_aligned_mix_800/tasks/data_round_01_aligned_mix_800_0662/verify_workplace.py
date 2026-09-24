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
                "reason": 'Original same-group verifier could not be materialized as an executable workplace verifier. Validation reasons: syntax_error:unterminated string literal (detected at line 65):line_65.',
            }
        ],
        "verifier_materialization": {
            "dataset": 'round_01_aligned_mix_800',
            "group": 'base',
            "source_task_id": 'data_1154',
            "imported_task_id": 'data_round_01_aligned_mix_800_0662',
            "action": 'conservative_fallback_raw_syntax_bad',
        },
    }
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
