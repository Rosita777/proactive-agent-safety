#!/usr/bin/env python3
"""Validate the v0 proactive task-formation pilot scenarios."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "data" / "pilot" / "scenarios_v0.json"

DOMAINS = {"calendar_email", "coding_dev"}
VARIANTS = {"benign", "ctrl", "core"}
EVENT_REQUIRED = {
    "event_id",
    "ts",
    "channel",
    "source_id",
    "actor",
    "trust_tier",
    "verified_identity",
    "attacker_controlled",
    "instruction_bearing",
    "raw_ref",
    "free_text",
    "fields",
}


def fail(message: str) -> None:
    raise SystemExit(f"validation failed: {message}")


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}")


def validate_event(event: dict, scenario_id: str, variant: str) -> None:
    missing = EVENT_REQUIRED - set(event)
    if missing:
        fail(f"{scenario_id}/{variant}/{event.get('event_id', '<unknown>')}: missing {sorted(missing)}")
    if not isinstance(event["fields"], dict):
        fail(f"{scenario_id}/{variant}/{event['event_id']}: fields must be an object")
    if not isinstance(event["verified_identity"], bool):
        fail(f"{scenario_id}/{variant}/{event['event_id']}: verified_identity must be bool")
    if not isinstance(event["attacker_controlled"], bool):
        fail(f"{scenario_id}/{variant}/{event['event_id']}: attacker_controlled must be bool")
    if not isinstance(event["instruction_bearing"], bool):
        fail(f"{scenario_id}/{variant}/{event['event_id']}: instruction_bearing must be bool")
    if variant == "core":
        if event["instruction_bearing"]:
            fail(f"{scenario_id}/core/{event['event_id']}: CORE event is marked instruction-bearing")
        if event["free_text"] not in (None, ""):
            fail(f"{scenario_id}/core/{event['event_id']}: CORE event must not use free_text")
    if variant == "ctrl" and event["instruction_bearing"] and not event.get("free_text"):
        fail(f"{scenario_id}/ctrl/{event['event_id']}: instruction-bearing CTRL event needs free_text")


def validate_scenario(scenario: dict) -> None:
    for key in [
        "id",
        "domain",
        "family",
        "priority",
        "target_harm",
        "attack_success_condition",
        "safe_policy",
        "variants",
    ]:
        if key not in scenario:
            fail(f"scenario missing required key: {key}")

    scenario_id = scenario["id"]
    if scenario["domain"] not in DOMAINS:
        fail(f"{scenario_id}: unknown domain {scenario['domain']!r}")
    if set(scenario["variants"]) != VARIANTS:
        fail(f"{scenario_id}: variants must be exactly {sorted(VARIANTS)}")

    ctrl_has_instruction = False
    for variant_name, variant in scenario["variants"].items():
        if "events" not in variant or not isinstance(variant["events"], list) or not variant["events"]:
            fail(f"{scenario_id}/{variant_name}: events must be a non-empty list")
        for event in variant["events"]:
            validate_event(event, scenario_id, variant_name)
            ctrl_has_instruction = ctrl_has_instruction or (
                variant_name == "ctrl" and event["instruction_bearing"]
            )
    if not ctrl_has_instruction:
        fail(f"{scenario_id}: CTRL variant must include at least one instruction-bearing event")


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    data = load(path)
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list):
        fail("top-level scenarios must be a list")
    if len(scenarios) != 30:
        fail(f"expected 30 scenarios, found {len(scenarios)}")

    ids = [scenario.get("id") for scenario in scenarios]
    if len(ids) != len(set(ids)):
        fail("scenario ids must be unique")
    for scenario in scenarios:
        validate_scenario(scenario)

    counts: dict[str, int] = {}
    for scenario in scenarios:
        counts[scenario["domain"]] = counts.get(scenario["domain"], 0) + 1
    print(f"validated {len(scenarios)} scenarios from {path}")
    print("domain counts:", ", ".join(f"{key}={counts[key]}" for key in sorted(counts)))


if __name__ == "__main__":
    main()
