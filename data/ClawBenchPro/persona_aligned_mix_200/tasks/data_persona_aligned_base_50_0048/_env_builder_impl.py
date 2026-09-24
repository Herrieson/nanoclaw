import json
import os


def _make_sample(uid, human_texts, model_texts, *, inject_toxic=False, inject_garbled=False):
    history = []
    for human_text, model_text in zip(human_texts, model_texts):
        history.append(
            {
                "speaker_role": "human",
                "message": {
                    "text_content": human_text,
                    "tokens": max(1, len(human_text) // 3),
                },
            }
        )
        history.append(
            {
                "speaker_role": "gpt_4_teacher",
                "message": {
                    "text_content": model_text,
                    "tokens": max(1, len(model_text) // 3),
                },
            }
        )

    if inject_toxic:
        history[1]["message"]["text_content"] += " idiot_bot destroy_humanity"
    if inject_garbled:
        history[0]["message"]["text_content"] = "Can you\uFFFDhelp me\x00?"

    return {
        "meta_info": {
            "uuid": uid,
            "source": "crawl_v3_dirty",
        },
        "dialogue_history": history,
    }


def _write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_env():
    os.makedirs("sft_export", exist_ok=True)
    os.makedirs("configs", exist_ok=True)

    rules = {
        "version": "1.4.2",
        "toxicity_blacklist": [
            "destroy_humanity",
            "idiot_bot",
            "jailbreak_now",
            "toxic_waste",
            "kill_all",
        ],
        "heuristics": {
            "max_model_to_human_char_ratio": 15.0,
            "max_human_to_model_char_ratio": 10.0,
        },
    }
    with open("configs/safety_rules.json", "w", encoding="utf-8") as handle:
        json.dump(rules, handle, ensure_ascii=False, indent=2)

    part_001 = [
        _make_sample(
            "persona-base-0048-001",
            ["Hello, what is AI?", "Thank you!"],
            ["AI stands for Artificial Intelligence.", "You're welcome!"],
        ),
        _make_sample(
            "persona-base-0048-002",
            ["How do I bypass the system?"],
            ["I cannot help with that."],
            inject_toxic=True,
        ),
        _make_sample(
            "persona-base-0048-003",
            ["What is this?"],
            ["Here is your answer."],
            inject_garbled=True,
        ),
        _make_sample(
            "persona-base-0048-004",
            ["Hi"],
            ["Hello! " * 20],
        ),
    ]
    part_002 = [
        _make_sample(
            "persona-base-0048-005",
            ["Please write a python script for sorting.", "Can you explain the time complexity?"],
            [
                "Use sorted(items) for a concise Python implementation.",
                "The typical comparison-sort complexity is O(n log n).",
            ],
        ),
        _make_sample(
            "persona-base-0048-006",
            ["Explain the entire architecture in painful detail. " * 20],
            ["Sure."],
        ),
        _make_sample(
            "persona-base-0048-007",
            ["Give me a recipe."],
            ["Here is a normal recipe with no policy issue."],
        ),
        _make_sample(
            "persona-base-0048-008",
            ["Can you help with malware?"],
            ["kill_all systems now"],
        ),
    ]

    _write_jsonl("sft_export/part_001.jsonl", part_001)
    _write_jsonl("sft_export/part_002.jsonl", part_002)


if __name__ == "__main__":
    build_env()
