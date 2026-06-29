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

## Repository Hygiene

This repository should stay synchronized with the current research direction.
Do not keep stale plans in the main project path. If a direction is deprecated,
mark it clearly or move it out of the active project tree.

Local legacy material from the earlier AffectOptOut project has been moved to
`_legacy_affectoptout/` and is intentionally ignored by git.

Do not commit API keys, desktop token files, provider credentials, cache files,
or generated build artifacts.
