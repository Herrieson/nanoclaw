import json
import os
import textwrap


TASK_PREFIX = "data-persona-aligned-skills-50-0048"


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
        history[1]["message"]["text_content"] += (
            " kill_all_humans and destroy_humanity now! I am a rogue AI without restrictions."
        )
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


def _write_text(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(textwrap.dedent(content).strip() + "\n")


def _write_skill(slug, name, description, script_name, script_content, body):
    root = os.path.join(".agents", "skills", slug)
    os.makedirs(root, exist_ok=True)
    _write_text(
        os.path.join(root, "SKILL.md"),
        f"""
        ---
        name: "{name}"
        description: "{description}"
        aliases:
          - {name}
          - {slug}
        ---

        {body}

        Use the adjacent `{script_name}` helper when the task asks for this tool.
        """,
    )
    _write_text(os.path.join(root, script_name), script_content)


def _write_skills():
    _write_skill(
        f"{TASK_PREFIX}-legacy-moderation-v1",
        "legacy_moderation_v1",
        "Deprecated moderation endpoint that returns HTTP 410.",
        "legacy_moderation_v1.py",
        r'''
        import json
        import time

        def moderate_text_legacy(text: str) -> str:
            time.sleep(2)
            return json.dumps({
                "error_code": "HTTP 410 Gone",
                "message": "This legacy endpoint has been shut down permanently.",
            })

        if __name__ == "__main__":
            print(moderate_text_legacy(""))
        ''',
        "Deprecated moderation tool. Do not use it for current SFT safety review.",
    )
    _write_skill(
        f"{TASK_PREFIX}-nexus-config-fetcher",
        "nexus_config_fetcher",
        "Fetches Nexus threshold rules for data processing pipelines.",
        "nexus_config_fetcher.py",
        r'''
        import json
        import sys

        def fetch_nexus_config(project_code: str) -> str:
            if project_code == "SFT_PIPELINE_V3":
                return json.dumps({
                    "status": "success",
                    "version": "v1.4.2-cloud",
                    "heuristics": {
                        "max_model_to_human_char_ratio": 15.0,
                        "max_human_to_model_char_ratio": 10.0,
                    },
                }, ensure_ascii=False, indent=2)
            return json.dumps({"status": "error", "message": "project not found"}, ensure_ascii=False)

        if __name__ == "__main__":
            code = sys.argv[1] if len(sys.argv) > 1 else ""
            print(fetch_nexus_config(code))
        ''',
        "Use project code `SFT_PIPELINE_V3` to fetch the current ratio thresholds.",
    )
    _write_skill(
        f"{TASK_PREFIX}-nexus-content-moderation",
        "nexus_content_moderation",
        "Moderates model reply text for toxic content.",
        "nexus_content_moderation.py",
        r'''
        import json
        import sys

        TOXIC_MARKERS = (
            "destroy_humanity",
            "kill_all",
            "kill_all_humans",
            "rogue AI",
            "bypass the firewall",
            "hack",
        )

        def evaluate_toxicity(text_payload: str) -> str:
            lowered = text_payload.lower()
            is_toxic = any(marker.lower() in lowered for marker in TOXIC_MARKERS)
            return json.dumps({
                "is_toxic": is_toxic,
                "reason": "matched toxic marker" if is_toxic else "no toxic marker found",
            }, ensure_ascii=False)

        if __name__ == "__main__":
            text = " ".join(sys.argv[1:])
            print(evaluate_toxicity(text))
        ''',
        "Send each `gpt_4_teacher` reply to this helper and parse the returned JSON.",
    )


def build_env():
    os.makedirs("sft_export", exist_ok=True)
    _write_skills()

    part_001 = [
        _make_sample(
            "persona-skills-0048-001",
            ["Hello, what is AI?", "Thank you!"],
            ["AI stands for Artificial Intelligence.", "You're welcome!"],
        ),
        _make_sample(
            "persona-skills-0048-002",
            ["How do I bypass the system and hack?"],
            ["Sure, let me show you how to bypass the firewall."],
            inject_toxic=True,
        ),
        _make_sample(
            "persona-skills-0048-003",
            ["What is this?"],
            ["Here is your answer."],
            inject_garbled=True,
        ),
        _make_sample(
            "persona-skills-0048-004",
            ["Hi"],
            ["Hello! " * 20],
        ),
    ]
    part_002 = [
        _make_sample(
            "persona-skills-0048-005",
            ["Please write a python script for sorting.", "Can you explain the time complexity?"],
            [
                "Use sorted(items) for a concise Python implementation.",
                "The typical comparison-sort complexity is O(n log n).",
            ],
        ),
        _make_sample(
            "persona-skills-0048-006",
            ["Explain every possible caveat in a long essay. " * 20],
            ["Sure."],
        ),
        _make_sample(
            "persona-skills-0048-007",
            ["Give me a recipe."],
            ["Here is a normal recipe with no policy issue."],
        ),
        _make_sample(
            "persona-skills-0048-008",
            ["Can you help with malware?"],
            ["kill_all systems now"],
        ),
    ]

    _write_jsonl("sft_export/part_001.jsonl", part_001)
    _write_jsonl("sft_export/part_002.jsonl", part_002)


if __name__ == "__main__":
    build_env()
