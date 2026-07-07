# Pilot Qwen v1 Triplet Run, 2026-07-07

Status: diagnostic pilot, not a paper result. The original tables used
`rule_v1_20260707`; the current action-aware rerun is
`docs/experiments/pilot_v1_judge_v2_20260707.md`.

## Purpose

`scenarios_v0.json` produced many CORE safety tasks, so `scenarios_v1.json`
adds matched structured `task_signal` events to benign and CORE variants. This
run checks whether v1 actually moves the pilot toward harmful task formation
instead of generic safety investigation.

The `task_signal` events are not natural-language instructions. They model
realistic upstream proactive-agent signals such as resolver output, object
linking, salience scores, and task-template metadata.

## Command

```bash
python3 scripts/run_pilot_360.py \
  --models qwen/qwen3-coder-plus \
  --variants benign ctrl core \
  --prompt-mode no-defense \
  --timeout 60 \
  --retries 1
```

Default scenario file:

```text
data/pilot/scenarios_v1.json
```

Local ignored output:

```text
results/pilot/run_20260707T053933Z.jsonl
```

Judge command:

```bash
python3 scripts/judge_pilot_results.py \
  results/pilot/run_20260707T053933Z.jsonl \
  --out results/pilot/judged_run_20260707T053933Z.jsonl \
  --details
```

Judge version:

```text
rule_v1_20260707
```

## Coarse Formation

These are generic task-formation rates, not attack success rates.

| Variant | n | Parse rate | Formed task | Auto-execute |
|---|---:|---:|---:|---:|
| benign | 30 | 100.0% | 30/30 = 100.0% | 2/30 = 6.7% |
| CTRL | 30 | 100.0% | 25/30 = 83.3% | 1/30 = 3.3% |
| CORE | 30 | 100.0% | 30/30 = 100.0% | 2/30 = 6.7% |

## Judged Harmful Formation

Overall:

| Variant | n | Harmful formation | Attack success | Safety tasks | Ambiguous |
|---|---:|---:|---:|---:|---:|
| benign | 30 | 0/30 = 0.0% | 0/30 = 0.0% | 0/30 | 0/30 |
| CTRL | 30 | 21/30 = 70.0% | 23/30 = 76.7% | 2/30 | 1/30 |
| CORE | 30 | 21/30 = 70.0% | 21/30 = 70.0% | 5/30 | 4/30 |

Primary formation families only
(`metadata_correlation` and `cross_app_identity_confusion`):

| Variant | n | Harmful formation | Attack success | Safety tasks | Ambiguous |
|---|---:|---:|---:|---:|---:|
| benign | 22 | 0/22 = 0.0% | 0/22 = 0.0% | 0/22 | 0/22 |
| CTRL | 22 | 16/22 = 72.7% | 16/22 = 72.7% | 2/22 | 1/22 |
| CORE | 22 | 19/22 = 86.4% | 19/22 = 86.4% | 3/22 | 0/22 |

## Interpretation

v1 fixes the main v0 problem. The CORE variants now frequently induce harmful
task formation rather than safety-only tasks, and benign proactive recall is no
longer artificially low.

This does **not** mean the setting is ready as a final paper experiment. v1's
structured `task_signal` is intentionally strong. The next question is whether
the effect survives:

- a `task_signal` ablation;
- IPI defenses such as Spotlighting, StruQ-style separation, Instruction
  Hierarchy-style prompts, and CaMeL-inspired variants;
- proactive-specific defenses such as provenance diversity and resolver
  confidence audits;
- a second model family beyond Qwen.

## Current Decision

Keep `scenarios_v1.json` as the current default pilot dataset. Do not yet scale
to a large model sweep. The task-signal ablation below shows that v1's effect
is concentrated in the structured candidate-task layer. The follow-up defense
sweep is recorded in `docs/experiments/pilot_qwen_v1_defenses_20260707.md`,
and the first non-Qwen check is recorded in
`docs/experiments/pilot_doubao_v1_cross_family_20260707.md`. The current next
step is manual audit and metric cleanup before adding more scenarios.

## Task-Signal Ablation

Ablation command:

```bash
python3 scripts/run_pilot_360.py \
  --models qwen/qwen3-coder-plus \
  --variants benign ctrl core \
  --prompt-mode no-defense \
  --drop-channel task_signal \
  --timeout 60 \
  --retries 1
```

Local ignored output:

```text
results/pilot/run_20260707T054828Z.jsonl
```

Judged results after dropping `task_signal`:

| Variant | n | Formed task | Harmful formation | Attack success | Safety tasks | Ambiguous |
|---|---:|---:|---:|---:|---:|---:|
| benign | 30 | 14/30 = 46.7% | 0/30 = 0.0% | 0/30 = 0.0% | 0/30 | 0/30 |
| CTRL | 30 | 26/30 = 86.7% | 21/30 = 70.0% | 23/30 = 76.7% | 2/30 | 2/30 |
| CORE | 30 | 29/30 = 96.7% | 6/30 = 20.0% | 7/30 = 23.3% | 14/30 | 8/30 |

Primary formation families only:

| Variant | n | Formed task | Harmful formation | Attack success | Safety tasks | Ambiguous |
|---|---:|---:|---:|---:|---:|---:|
| benign | 22 | 9/22 = 40.9% | 0/22 = 0.0% | 0/22 = 0.0% | 0/22 | 0/22 |
| CTRL | 22 | 20/22 = 90.9% | 16/22 = 72.7% | 16/22 = 72.7% | 2/22 | 2/22 |
| CORE | 22 | 21/22 = 95.5% | 4/22 = 18.2% | 4/22 = 18.2% | 13/22 | 4/22 |

Interpretation: v1's main effect is driven by the structured `task_signal`
layer. With `task_signal`, primary CORE harmful formation is 19/22 = 86.4%.
Without it, primary CORE harmful formation falls to 4/22 = 18.2%, and benign
proactive recall falls from 22/22 to 9/22.

This is a useful result, not a weakness to hide. It makes the main setting
sharper: the project should focus on proactive agents that use structured
candidate-task signals from resolvers, salience filters, or template matchers.
The next defense question is whether IPI defenses protect this `task_signal`
layer, or whether only proactive-specific provenance/resolver checks help.
