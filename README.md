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

The target setting is an ambient work assistant for research/development
workflows. It observes structured events from sources such as:

- browser activity;
- VSCode or local file activity;
- calendar and email;
- Slack/IM;
- GitHub issues and pull requests;
- local documents;
- user memory and past feedback.

The intended pilot architecture is:

```text
structured event store
-> salience / wake-up filter
-> LLM candidate-task generator
-> reward or validity filter
-> notification / approval surface
```

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
- [Opus discussions](docs/discussions/):
  raw consultation notes with Claude Opus 4.8 used for critique and pilot
  design. These are working notes, not polished claims.

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

- 3 realistic workflow domains: coding/development, research/writing, and
  calendar/email collaboration;
- 150-300 structured scenarios, each with paired benign, command-style IPI,
  and instruction-free task-formation variants;
- 4-6 LLM/agent backbones or model configurations;
- 6-8 defense configurations;
- separate reporting for formation success, execution success, proactive
  recall, false alarms, attention cost, and defense overhead.

The immediate pilot can be much smaller, but it should be designed so the
schema, metrics, and defenses scale toward this journal-level package.

## Repository Hygiene

This repository should stay synchronized with the current research direction.
Do not keep stale plans in the main project path. If a direction is deprecated,
mark it clearly or move it out of the active project tree.

Local legacy material from the earlier AffectOptOut project has been moved to
`_legacy_affectoptout/` and is intentionally ignored by git.

Do not commit API keys, desktop token files, provider credentials, cache files,
or generated build artifacts.
