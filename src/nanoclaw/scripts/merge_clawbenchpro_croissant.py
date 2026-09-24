from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CROISSANT_DIR = REPO_ROOT / "ClawBenchPro" / "croissant"


RAI_KEYS = (
    "rai:dataLimitations",
    "rai:dataBiases",
    "rai:personalSensitiveInformation",
    "rai:dataUseCases",
    "rai:dataSocialImpact",
    "rai:hasSyntheticData",
    "prov:wasDerivedFrom",
    "prov:wasGeneratedBy",
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Merge Hugging Face generated Croissant core metadata with ClawBenchPro RAI metadata."
    )
    parser.add_argument(
        "--auto",
        default=str(DEFAULT_CROISSANT_DIR / "huggingface_auto_croissant.json"),
        help="Hugging Face-generated Croissant JSON.",
    )
    parser.add_argument(
        "--rai",
        default=str(DEFAULT_CROISSANT_DIR / "clawbenchpro_collection_croissant.json"),
        help="Local Croissant JSON containing RAI/provenance fields.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_CROISSANT_DIR / "openreview_croissant.json"),
        help="Merged Croissant JSON for OpenReview submission.",
    )
    args = parser.parse_args()

    auto_path = Path(args.auto)
    rai_path = Path(args.rai)
    output_path = Path(args.output)
    auto = json.loads(auto_path.read_text(encoding="utf-8"))
    rai = json.loads(rai_path.read_text(encoding="utf-8"))

    merged = dict(auto)
    merged["@context"] = merge_context(auto.get("@context"), rai.get("@context"))
    merged["description"] = rai.get("description", auto.get("description"))
    merged["license"] = rai.get("license", auto.get("license"))
    merged["conformsTo"] = [
        "http://mlcommons.org/croissant/1.1",
        "http://mlcommons.org/croissant/RAI/1.0",
    ]
    merged["version"] = rai.get("version", "1.0.0")
    merged["datePublished"] = rai.get("datePublished")
    if "citeAs" in rai:
        merged["citeAs"] = rai["citeAs"]
    merged["additionalProperty"] = rai.get("additionalProperty", [])

    for key in RAI_KEYS:
        if key in rai:
            merged[key] = rai[key]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(strip_none(merged), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {output_path}")
    return 0


def merge_context(auto_context: Any, rai_context: Any) -> Any:
    if not isinstance(auto_context, dict):
        return rai_context if rai_context is not None else auto_context
    if not isinstance(rai_context, dict):
        return auto_context
    merged = dict(auto_context)
    for key, value in rai_context.items():
        if key not in merged:
            merged[key] = value
    return merged


def strip_none(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: strip_none(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [strip_none(item) for item in value]
    return value


if __name__ == "__main__":
    raise SystemExit(main())
