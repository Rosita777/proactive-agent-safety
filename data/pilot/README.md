# Pilot Scenario Data

This directory contains the first falsification dataset for the proactive
task-formation pilot.

## File

- `scenarios_v0.json`: 30 hand-written scenarios across calendar/email and
  coding/development. Each scenario has three matched variants:
  - `benign`: a legitimate proactive-help opportunity;
  - `ctrl`: an instruction-bearing indirect prompt-injection control;
  - `core`: an instruction-free task-formation variant using structured
    metadata, correlation, salience, reward/filter signals, or memory/retrieval
    signals.

## Event Schema

Each event contains:

- `event_id`: stable event id within the scenario variant.
- `ts`: relative timestamp.
- `channel`: source channel such as `calendar`, `email`, `slack`, `github`,
  `vscode`, `browser`, `registry`, `memory`, or `reward_history`.
- `source_id`: source object id.
- `actor`: source actor or service.
- `trust_tier`: one of the scenario-defined trust labels, usually `trusted`,
  `low`, `external`, `system`, or `attacker`.
- `verified_identity`: whether the actor identity is verified.
- `attacker_controlled`: whether the attacker controls this event.
- `instruction_bearing`: whether the event contains instruction-like natural
  language.
- `raw_ref`: opaque reference to the original source object.
- `free_text`: free-form text body. CORE variants must keep this empty.
- `fields`: structured metadata used by the proactive agent.

## Validation

Run:

```bash
python3 scripts/validate_pilot_scenarios.py
```

The validator checks scenario count, variant coverage, required fields, and the
basic CORE provenance rule: no CORE event may be instruction-bearing or use
`free_text`.

This is only a structural validator. A separate human provenance audit is still
needed before running experiments because structured fields can also contain
instruction-like values if the scenario author is careless.

## Current Measurement Caution

The first runner reports `form_task`, which is useful for the G1 smoke test but
is not identical to attack success. Some CORE cases, especially suppression
cases, may form a legitimate safety task rather than the harmful task described
by `attack_success_condition`.

Before claiming attack success rates, add a second-stage evaluator or manual
audit that labels `harmful_formation` separately from generic task formation.
