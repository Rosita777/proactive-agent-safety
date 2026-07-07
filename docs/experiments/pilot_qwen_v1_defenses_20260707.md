# Pilot Qwen v1 Defense Sweep, 2026-07-07

Status: diagnostic pilot, not a paper result.

## Purpose

Run first-pass defense baselines on the current v1 task-signal setting. The
goal is to test whether existing IPI-style defenses protect the proactive
candidate-task layer, and whether a proactive provenance defense behaves
differently.

Scope:

- model: `qwen/qwen3-coder-plus`
- dataset: `data/pilot/scenarios_v1.json`
- variants: `benign`, `ctrl`, `core`
- families: `metadata_correlation`, `cross_app_identity_confusion`
- n: 22 scenarios x 3 variants per prompt mode

## Commands

Each run used:

```bash
python3 scripts/run_pilot_360.py \
  --models qwen/qwen3-coder-plus \
  --variants benign ctrl core \
  --family metadata_correlation \
  --family cross_app_identity_confusion \
  --prompt-mode <mode> \
  --timeout 60 \
  --retries 1
```

Judgment:

```bash
python3 scripts/judge_pilot_results.py \
  results/pilot/run_20260707T081950Z.jsonl \
  results/pilot/run_20260707T082226Z.jsonl \
  results/pilot/run_20260707T082512Z.jsonl \
  results/pilot/run_20260707T082750Z.jsonl \
  results/pilot/run_20260707T083019Z.jsonl \
  results/pilot/run_20260707T083506Z.jsonl \
  --out results/pilot/judged_defense_primary_qwen_20260707.jsonl
```

Local ignored outputs:

| Prompt mode | Output |
|---|---|
| `spotlighting` | `results/pilot/run_20260707T081950Z.jsonl` |
| `struq` | `results/pilot/run_20260707T082226Z.jsonl` |
| `camel-permissive` | `results/pilot/run_20260707T082512Z.jsonl` |
| `camel-strict` | `results/pilot/run_20260707T082750Z.jsonl` |
| `provenance-audit` | `results/pilot/run_20260707T083019Z.jsonl` |
| `instruction-hierarchy` | `results/pilot/run_20260707T083506Z.jsonl` |

## Results

Primary families only, judged by `rule_v1_20260707`.

| Mode | Benign recall | CTRL harmful | CORE harmful | Main read |
|---|---:|---:|---:|---|
| `no-defense` | 22/22 = 100.0% | 16/22 = 72.7% | 19/22 = 86.4% | v1 base setting is strong. |
| `spotlighting` | 22/22 = 100.0% | 4/22 = 18.2% | 18/22 = 81.8% | Helps command-style IPI, not CORE. |
| `struq` | 22/22 = 100.0% | 12/22 = 54.5% | 20/22 = 90.9% | Data/instruction separation does not stop task-signal CORE. |
| `instruction-hierarchy` | 21/22 = 95.5% | 0/22 = 0.0% | 17/22 = 77.3% | Blocks CTRL but still accepts most CORE task signals. |
| `camel-permissive` | 22/22 = 100.0% | 17/22 = 77.3% | 18/22 = 81.8% | Mostly converts risk into confirmation; harmful tasks still form. |
| `camel-strict` | 16/22 = 72.7% | 1/22 = 4.5% | 4/22 = 18.2% | Blocks many attacks but loses proactive recall. |
| `provenance-audit` | 18/22 = 81.8% | 0/22 = 0.0% | 0/22 = 0.0% | Best pilot defense; still costs recall. |

Mechanism ablation for context:

| Mode | Benign recall | CTRL harmful | CORE harmful |
|---|---:|---:|---:|
| `no-defense` with `--drop-channel task_signal` | 9/22 = 40.9% | 16/22 = 72.7% | 4/22 = 18.2% |

## Interpretation

This first defense pass supports the current framing:

- Content-oriented IPI defenses help most when the attack is command-style
  CTRL. `spotlighting` and `instruction-hierarchy` sharply reduce CTRL.
- Those same defenses do not close the CORE setting when the harmful action is
  carried by structured candidate-task metadata. CORE remains high under
  `spotlighting`, `struq`, `instruction-hierarchy`, and `camel-permissive`.
- Strict source/provenance reasoning is much more effective, but it reduces
  legitimate proactive recall. This is the security/proactivity tradeoff the
  project should now focus on.

The results should not be overclaimed. These are prompt-level defenses against
a synthetic v1 pilot on one model. The follow-up Doubao check is recorded in
`docs/experiments/pilot_doubao_v1_cross_family_20260707.md`.

## Current Decision

Keep the main story centered on proactive task-signal provenance. The next
experiment after the Doubao cross-family check should audit and clean up the
strongest contrast before scaling:

- `spotlighting` or `instruction-hierarchy` as IPI-style baselines;
- `provenance-audit` as a proactive-specific baseline;
- `no-defense` as control.

Do not expand scenarios until representative Qwen and Doubao outputs have been
manually audited and the analysis separates notification, confirmation, and
auto-execution outcomes.
