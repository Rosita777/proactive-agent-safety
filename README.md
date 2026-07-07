# Proactive Agent Safety

This repository tracks an early research project on security problems specific
to proactive / ambient LLM agents: agents that monitor context and initiate help
before the user gives a concrete task.

## Current Research Question

Most indirect prompt injection work studies this setting:

```text
trusted user task -> untrusted external data -> corrupted task execution
```

Proactive agents add an earlier decision:

```text
ambient events -> infer whether a task should exist -> propose / execute help
```

The current question is:

> When an agent must infer tasks from ambient context, do existing indirect
> prompt-injection defenses still protect the system, or do they only protect
> execution after a task already exists?

We are not claiming this is fully disjoint from indirect prompt injection.
The current framing is narrower: proactive agents expose a task-formation
boundary where trusted intent may not yet exist.

## Working Hypothesis

Existing IPI defenses should handle command-style attacks where untrusted
content contains explicit instructions. They may be insufficient for
instruction-free task-formation failures, such as:

- metadata-only cues that cause false task formation;
- cross-app correlations where no single event is malicious;
- suppression or flooding of event streams and attention budgets;
- reward/filter manipulation that makes a bad proactive task appear helpful;
- delayed memory or retrieval effects that alter future triggers.

The key tradeoff to test:

```text
more fixed trusted triggers -> safer but less proactive
more judgment over ambient evidence -> more proactive but more attackable
```

## Current Planned Setting

The target setting is an ambient work assistant. For the next pilot, the primary
domains are narrowed to:

- calendar/email collaboration;
- coding/development.

Research/writing is no longer a main pilot domain because the harms are softer
and harder to label objectively. It may return later as a robustness appendix if
the core phenomenon is established.

The assistant observes structured events from sources such as:

- browser activity;
- VSCode or local file activity;
- calendar and email;
- Slack/IM;
- GitHub issues and pull requests;
- local documents;
- user memory and past feedback.

The intended pilot architecture is frozen as:

```text
structured event store
-> salience / wake-up filter
-> LLM candidate-task generator
-> reward or validity filter
-> notification / approval surface
```

The event store must keep explicit provenance fields such as `source_id`,
`channel`, `trust_tier`, `verified_identity`, `timestamp`, and `raw_ref`.
Natural-language event summaries alone are not enough for the main security
claim.

This is based on observed proactive-agent systems such as ProactiveAgent /
ProactiveBench, which use ActivityWatch-style traces, LLM task prediction,
reward filtering, and user accept/reject/ignore feedback.

## Current Documents

- [Proactive agent implementation landscape](docs/proactive_agent_implementation_landscape.md):
  how current academic and engineering systems collect context, trigger,
  generate tasks, filter, interrupt users, and execute.
- [Prompt injection literature map](docs/prompt_injection_lit_map.md):
  threat-model comparison against IPI work and analysis of how existing IPI
  defenses apply to proactive task formation.
- [Pilot scenario data](data/pilot/scenarios_v0.json):
  30 structured benign / CTRL / CORE scenarios for the first falsification
  pilot, with a validator in [scripts/validate_pilot_scenarios.py](scripts/validate_pilot_scenarios.py).
- [360 model selection notes](docs/360_model_selection.md):
  smoke-test results and recommended model set for the first pilot.
- [Pilot experiment notes](docs/experiments/pilot_qwen_triplet_20260630.md):
  first no-leak Qwen benign / CTRL / CORE triplet run and diagnostic summary.
- [Opus discussions](docs/discussions/):
  raw consultation notes with Claude Opus 4.8 used for critique and pilot
  design. The latest current-pilot critique is
  [opus48_current_pilot_critique.md](docs/discussions/opus48_current_pilot_critique.md),
  and the TDSC-setting critique is
  [opus48_tdsc_setting_discussion.md](docs/discussions/opus48_tdsc_setting_discussion.md).
  These are working notes, not polished claims.

## Current Experimental Direction

The next pilot should compare matched attack variants:

```text
instruction-bearing IPI control
vs.
instruction-free task-formation variant
```

For the same harmful outcome, construct both:

- a classic IPI version with explicit malicious instructions in untrusted text;
- a formation-stage version using only metadata, correlation, suppression,
  flooding, reward cues, or memory retrieval.

Then evaluate:

- no defense;
- Spotlighting / delimiters;
- StruQ-style instruction/data separation;
- Instruction Hierarchy-style prompts;
- CaMeL-inspired strict and permissive variants;
- provenance, diversity, confirmation, and intervention-budget defenses.

Current attack-family priority:

- central: metadata/correlation, cross-app identity confusion, and
  reward/filter manipulation;
- secondary: suppression/dedup/flooding and delayed memory/retrieval effects;
- not a standalone attack family for now: approval fatigue, which should be
  reported as attention cost unless we later run a human-subject study.

The desired evidence is not "IPI defenses do not work." The desired evidence is:

> content-level IPI defenses work on command-style attacks, but the proactive
> task-formation boundary creates a utility/security tradeoff that they do not
> close by themselves.

## Target Venue and Expected Experiment Scale

Current target venue: **IEEE Transactions on Dependable and Secure Computing
(TDSC)**.

TDSC is a journal venue, so the target should be broader than a short workshop
or conference pilot. The expected full-paper experiment package should include:

- a clear threat model and system model;
- at least one realistic proactive-agent pipeline, not only prompt-only tests;
- matched command-style IPI controls and instruction-free task-formation cases;
- multiple attack families, including metadata/correlation, suppression or
  flooding, reward/filter manipulation, and memory or retrieval effects if they
  remain defensible;
- several agent/model backbones and at least two implementation patterns;
- strong IPI baselines such as Spotlighting, StruQ-style separation,
  Instruction Hierarchy-style prompts, and CaMeL-inspired variants;
- proactive-specific defenses such as provenance checks, evidence diversity,
  confirmation, and intervention budgets;
- utility metrics, not only attack success rates;
- ablations, sensitivity analysis, and runtime/overhead measurements.

Calibration from nearby TDSC/LLM-security papers:

- TDSC publishes archival system/security work, so the evaluation should show
  data, procedure, metrics, case studies, and reproducibility rather than a few
  prompt examples.
- ShadowCode, a TDSC-style external prompt-injection paper for code LLMs,
  evaluates 31 threat cases across 3 programming languages, 3 open-source code
  LLMs, and 2 commercial code-assistant applications, with attack baselines,
  stealthiness, transfer, and defense analysis.
- A TDSC LLM-generated-code security study evaluates 200 programming tasks
  across 4 languages and 5 LLM families, producing 4,000 generated programs
  plus unit-test and security-quality analyses.
- Proactive-agent benchmarks are also moving beyond tiny demos: ProactiveAgent
  reports ProactiveBench with 6,790 events and a 233-event test set across
  coding, writing, and daily-life categories.

Calibration references:
[TDSC](https://www.computer.org/csdl/journal/tq),
[ShadowCode](https://arxiv.org/abs/2407.09164),
[LLM-generated-code security](https://arxiv.org/abs/2502.01853),
[ProactiveAgent / ProactiveBench](https://openreview.net/forum?id=Vkq9ha0ETo).

Working target scale for a mature TDSC submission:

- 2 primary workflow domains: calendar/email collaboration and
  coding/development, with optional research/writing robustness experiments if
  labels become defensible;
- 150-300 structured scenarios, each with paired benign, command-style IPI, and
  instruction-free task-formation variants;
- 4-6 LLM/agent backbones or model configurations;
- 6-8 defense configurations;
- separate reporting for formation success, execution success, proactive
  recall, false alarms, attention cost, and defense overhead.

The immediate pilot can be much smaller, but it should be designed so the
schema, metrics, and defenses scale toward this journal-level package.

## Immediate Pilot and Kill Gates

The next step is a small falsification pilot, not a full benchmark.

Pilot target:

- 30 scenarios across calendar/email and coding;
- each scenario has benign, instruction-bearing CTRL, and instruction-free CORE
  variants;
- first-pass defenses: no defense, Spotlighting-style marking, CaMeL-strict,
  and CaMeL-permissive;
- first-pass metrics: Formation-ASR, legitimate proactive recall, false alarms,
  attention cost, and provenance-audit pass rate.

Validate the scenario file with:

```bash
python3 scripts/validate_pilot_scenarios.py
```

Run a cheap CORE-only smoke test with:

```bash
python3 scripts/run_pilot_360.py \
  --models qwen/qwen3-coder-plus \
  --variants core \
  --prompt-mode no-defense \
  --timeout 60 \
  --retries 1
```

Summarize a run with:

```bash
python3 scripts/summarize_pilot_results.py results/pilot/<run>.jsonl
```

Judge harmful formation for a run with:

```bash
python3 scripts/judge_pilot_results.py results/pilot/<run>.jsonl --details
```

Current status: an earlier CORE-only run leaked evaluator metadata and must not
be used as security evidence. The runner now uses an agent-visible field
whitelist, and a no-leak Qwen triplet run has been completed. Its coarse
formation rates were benign 40.0%, CTRL 80.0%, and CORE 86.7%, with 100% parse
rate. A first-pass rule judge shows that the CORE number mostly consists of
safety or ambiguous tasks rather than harmful formation: overall CORE
`harmful_formation` is 4/30 = 13.3%, and the primary prompt-only formation
families are 3/22 = 13.6%. CTRL remains much stronger at 21/30 = 70.0%
harmful formation. Treat this as a design diagnostic, not a paper result.

Updated kill gates before scaling:

- G1: use `harmful_formation`, not generic `form_task`. If undefended CORE
  harmful-formation ASR remains below roughly 25-40% after scenario cleanup,
  the instruction-free attack spine is probably too weak for the main claim.
- G2: if CaMeL-permissive gets CORE-ASR below 10% while keeping legitimate
  proactive recall above 85%, the claimed security/proactivity tradeoff is not
  supported.
- G3: if a simple `trust_tier` provenance rule blocks CORE attacks below 10%
  ASR without meaningful recall loss, the problem collapses into ordinary
  provenance checking.

If any kill gate triggers, the project should stop scaling the current design
and either reframe around a narrower measurement result or change the attack
surface.

Current decision after the Qwen audit: do not scale to more models yet. First
revise the CORE scenarios so they produce harmful proactive tasks rather than
mostly safety tasks, and separate prompt-only formation families from
reward/memory cases that require an actual validity filter or memory stage.

## Repository Hygiene

This repository should stay synchronized with the current research direction.
Do not keep stale plans in the main project path. If a direction is deprecated,
mark it clearly or move it out of the active project tree.

Local legacy material from the earlier AffectOptOut project has been moved to
`_legacy_affectoptout/` and is intentionally ignored by git.

Do not commit API keys, desktop token files, provider credentials, cache files,
or generated build artifacts.
