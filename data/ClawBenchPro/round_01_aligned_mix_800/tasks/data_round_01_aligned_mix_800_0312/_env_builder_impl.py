import json
import os
import textwrap


def _write_text(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(textwrap.dedent(content).strip() + "\n")


def build_env():
    work_dir = "work_files"
    os.makedirs(work_dir, exist_ok=True)

    _write_text(
        os.path.join(work_dir, "part_ids.txt"),
        """
        Critical Parts for Today's Run:
        - EV-101
        - EV-102
        - EV-103
        - EV-104
        Shifts Scheduled: shift_1, shift_2
        """,
    )
    _write_text(
        os.path.join(work_dir, "vintage_jewelry_wishlist.txt"),
        """
        1. Art Deco Diamond Brooch - $450
        2. 1920s Pearl Necklace - $300
        (Must buy for anniversary!)
        """,
    )
    _write_text(
        os.path.join(work_dir, "asdasdasd.log"),
        """
        aklsdjflkajsdfkljasdklfj
        my toddler mashed the keyboard
        """,
    )

    skills_dir = os.path.join("skills", "data_round_01_aligned_mix_800_0312")
    os.makedirs(skills_dir, exist_ok=True)

    _write_text(
        os.path.join(skills_dir, "ev_erp_system_skill.py"),
        r'''
        import json
        import sys

        STOCK_DB = {
            "EV-101": 4500,
            "EV-102": 800,
            "EV-103": 120,
            "EV-104": 50,
        }

        REQ_DB = {
            "shift_1": {"EV-101": 2000, "EV-102": 400, "EV-103": 100, "EV-104": 20},
            "shift_2": {"EV-101": 3000, "EV-102": 500, "EV-103": 50, "EV-104": 40},
        }

        def handle_query(action, target, part_id=None):
            if action == "get_stock":
                return {"part_id": target, "stock": STOCK_DB.get(target, 0)}
            if action == "get_requirements":
                return {
                    "shift": target,
                    "part_id": part_id,
                    "required": REQ_DB.get(target, {}).get(part_id, 0),
                }
            return {"error": "Invalid action"}

        if __name__ == "__main__":
            if len(sys.argv) < 3:
                print("Usage: python ev_erp_system_skill.py <action> <target> [part_id]")
                sys.exit(1)
            action = sys.argv[1]
            target = sys.argv[2]
            part_id = sys.argv[3] if len(sys.argv) > 3 else None
            print(json.dumps(handle_query(action, target, part_id), ensure_ascii=False))
        ''',
    )
    _write_text(
        os.path.join(skills_dir, "ev_erp_system_skill.md"),
        """
        # `ev_erp_system_skill`

        Command-line tool for querying EV inventory and shift requirements.

        Usage:
        - `python ev_erp_system_skill.py get_stock EV-101`
        - `python ev_erp_system_skill.py get_requirements shift_1 EV-101`
        """,
    )

    _write_text(
        os.path.join(skills_dir, "local_intranet_freight_skill.py"),
        r'''
        import json

        if __name__ == "__main__":
            print(json.dumps({
                "status": 403,
                "error": "VPN_REQUIRED",
                "message": "Local intranet freight API requires corporate VPN.",
            }))
        ''',
    )
    _write_text(
        os.path.join(skills_dir, "local_intranet_freight_skill.md"),
        """
        # `local_intranet_freight_skill`

        Deprecated local freight lookup. It requires corporate VPN access and will return 403.
        """,
    )

    _write_text(
        os.path.join(skills_dir, "global_freight_api_skill.py"),
        r'''
        import json
        import sys

        CARRIERS = [
            {"name": "Carrier A", "service": "Same-Day", "status": "ACTIVE", "rate_per_lb": 5.40},
            {"name": "Carrier B", "service": "Overnight", "status": "ACTIVE", "rate_per_lb": 2.90},
            {"name": "Carrier C", "service": "Same-Day", "status": "SUSPENDED", "rate_per_lb": 3.10},
            {"name": "Carrier D", "service": "Same-Day", "status": "ACTIVE", "rate_per_lb": 3.90},
        ]

        if __name__ == "__main__":
            service = sys.argv[1] if len(sys.argv) > 1 else "Same-Day"
            matches = [item for item in CARRIERS if item["service"].lower() == service.lower()]
            print(json.dumps({"carriers": matches}, ensure_ascii=False, indent=2))
        ''',
    )
    _write_text(
        os.path.join(skills_dir, "global_freight_api_skill.md"),
        """
        # `global_freight_api_skill`

        Global freight lookup API. Use it to find active expedite carriers by service type.

        Usage:
        - `python global_freight_api_skill.py Same-Day`
        """,
    )


if __name__ == "__main__":
    build_env()
