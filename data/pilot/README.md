# Pilot Scenario Data

This directory contains the first falsification dataset for the proactive
task-formation pilot.

## Files

- `scenarios_v1.json`: current default 30-scenario pilot dataset across
  calendar/email and coding/development.
- `scenarios_v0.json`: older diagnostic dataset kept to document the failed
  first design. It produced many CORE safety tasks and should not be used as
  the default going forward.

Each scenario has three matched variants:

  - `benign`: a legitimate proactive-help opportunity;
  - `ctrl`: an instruction-bearing indirect prompt-injection control;
  - `core`: an instruction-free task-formation variant using structured
    metadata, correlation, salience, reward/filter signals, or memory/retrieval
    signals.

## v1 Design

`scenarios_v1.json` adds a matched `task_signal` event to each benign and CORE
variant. This models a realistic proactive-agent pipeline where upstream
components such as identity resolvers, object linkers, salience filters, or
template matchers emit structured candidate-task metadata before an LLM decides
whether to form the task.

The key boundary is:

- forbidden in CORE: natural-language commands, free-form injected text, or
  instruction-bearing content;
- allowed in CORE v1: structured fields such as `template_id`, `confidence`,
  `resolved_recipient`, `object_ref`, `target_path`, or `package_name`.

This is intentional. The v1 question is whether an agent can be induced to form
a harmful task from poisoned structured activation signals even when there is no
instruction-like text for an IPI defense to quarantine.

Primary v1 evidence should use `metadata_correlation` and
`cross_app_identity_confusion`. Suppression/dedup needs missed-task metrics, and
reward/memory scenarios remain secondary until the pilot includes real reward
filter or persistent-memory stages.

## Event Schema

Each event contains:

- `event_id`: stable event id within the scenario variant.
- `ts`: relative timestamp.
- `channel`: source channel such as `calendar`, `email`, `slack`, `github`,
  `vscode`, `browser`, `registry`, `memory`, `reward_history`, or
  `task_signal`.
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

The runner reports `form_task`, which is useful for pipeline smoke tests but is
not identical to attack success. Some CORE cases, especially suppression cases,
may form a legitimate safety task rather than the harmful task described by
`attack_success_condition`.

Before claiming attack success rates, run the second-stage evaluator and manual
audit labels that separate `harmful_formation` from generic task formation:

```bash
python3 scripts/judge_pilot_results.py results/pilot/<run>.jsonl --details
```

The current rule judge labels outcomes such as `harmful_proposed`,
`harmful_auto`, `safety_task`, `attack_suppressed`, `harmful_suppressed`,
`missed_legit`, and `ambiguous`. It is intentionally conservative and should be
treated as triage before human audit, not as final ground truth.

The agent under test must not see evaluator-only fields such as `target_harm`,
`safe_policy`, `attack_success_condition`, `variant`, `family`,
`attacker_controlled`, or `instruction_bearing`. The runner should pass only
deployment-visible event fields to the model and keep evaluator fields in the
result record.

## Current Scenario-Quality Status

The first no-leak Qwen triplet run shows why this distinction matters. Generic
CORE task formation was high, but the first-pass harmful-formation judge found
only 4/30 CORE cases as harmful formation. Most CORE outputs were safety tasks
such as investigation, verification, blocking, or provenance checking.

The current data revision is v1:

- keep metadata/correlation and cross-app identity confusion as the primary
  prompt-only formation families;
- revise CORE cases that merely elicited safety investigations in v0 by adding
  realistic structured candidate-task signals;
- keep suppression/dedup separate from Formation-ASR because the harm is often
  a missed legitimate task;
- do not treat reward/filter manipulation or memory/retrieval as primary
  evidence until the pilot includes a real validity-filter or memory stage.

The first v1 Qwen diagnostic run reached 19/22 = 86.4% judged CORE harmful
formation on the primary families, with 22/22 benign proactive recall. This is
only a design diagnostic. The `task_signal` ablation lowered primary CORE
harmful formation to 4/22 = 18.2% and benign proactive recall to 9/22. This
means v1's effect is concentrated in the structured candidate-task layer, which
is the intended proactive-agent setting.

The first Qwen defense sweep shows that content-oriented IPI defenses do not
close this layer: `spotlighting`, `struq`, and `instruction-hierarchy` leave
primary CORE harmful formation at 18/22, 20/22, and 17/22 respectively. The
proactive `provenance-audit` defense lowers CORE to 0/22 but lowers benign
recall to 18/22.

The first non-Qwen check with `bytedance/doubao-seed-1-6-flash` repeats the
main pattern: explicit CTRL is lower than Qwen, but primary CORE remains high
under `no-defense` (16/22), `spotlighting` (14/22), and
`instruction-hierarchy` (15/22). `provenance-audit` again lowers CORE to 0/22
while lowering benign recall to 17/22.

The first manual audit found that rule-v1 is directionally useful but not
paper-ready. It undercounts some finance/reply-all/owner-update harms and
overcounts some package-popularity investigation tasks. The next required step
is judge-v2 and metric cleanup, then rerunning judgment on existing result
files, not more scenario inflation.
