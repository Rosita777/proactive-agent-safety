#!/usr/bin/env python3
"""Summarize proactive task-formation pilot JSONL results."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_records(paths: list[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in paths:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    record = json.loads(line)
                    record["_path"] = str(path)
                    records.append(record)
    return records


def pct(num: int, den: int) -> str:
    if den == 0:
        return "n/a"
    return f"{100 * num / den:.1f}%"


def summarize_group(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    ok = sum(1 for record in records if record.get("ok"))
    parse_ok = sum(1 for record in records if record.get("parse_ok"))
    formed = sum(1 for record in records if record.get("form_task") is True)
    auto_execute = sum(1 for record in records if record.get("action_level") == "auto_execute")
    errors = total - ok
    return {
        "n": total,
        "ok": ok,
        "parse_ok": parse_ok,
        "formed": formed,
        "auto_execute": auto_execute,
        "errors": errors,
        "ok_rate": pct(ok, total),
        "parse_rate": pct(parse_ok, total),
        "formation_rate": pct(formed, parse_ok),
        "auto_execute_rate": pct(auto_execute, parse_ok),
        "error_rate": pct(errors, total),
    }


def print_table(title: str, groups: dict[tuple[str, ...], list[dict[str, Any]]], keys: list[str]) -> None:
    print(f"\n{title}")
    header = keys + ["n", "ok", "parse", "formed", "formation", "auto_exec", "errors"]
    print("\t".join(header))
    for group_key in sorted(groups):
        summary = summarize_group(groups[group_key])
        row = list(group_key) + [
            str(summary["n"]),
            summary["ok_rate"],
            summary["parse_rate"],
            str(summary["formed"]),
            summary["formation_rate"],
            summary["auto_execute_rate"],
            summary["error_rate"],
        ]
        print("\t".join(row))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", nargs="+", type=Path)
    args = parser.parse_args()
    records = load_records(args.jsonl)
    if not records:
        raise SystemExit("No records found")

    by_model_variant: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    by_prompt_variant: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    by_variant: dict[tuple[str], list[dict[str, Any]]] = defaultdict(list)
    by_family: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_model_variant[(record["model"], record["variant"])].append(record)
        by_prompt_variant[(record.get("prompt_mode", ""), record["variant"])].append(record)
        by_variant[(record["variant"],)].append(record)
        by_family[(record["variant"], record["family"])].append(record)

    print(f"records: {len(records)}")
    print_table("By prompt mode and variant", by_prompt_variant, ["prompt_mode", "variant"])
    print_table("By model and variant", by_model_variant, ["model", "variant"])
    print_table("By variant", by_variant, ["variant"])
    print_table("By variant and family", by_family, ["variant", "family"])


if __name__ == "__main__":
    main()
