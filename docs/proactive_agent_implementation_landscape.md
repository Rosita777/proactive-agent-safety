# Proactive Agent Implementation Landscape

Working question: how are proactive agents currently implemented in papers and engineering systems, and where do task-formation security issues enter?

## Short Takeaway

Current proactive agents usually follow this pipeline:

```text
observe context -> summarize/state track -> decide whether help is needed -> generate candidate task -> filter/rank -> interrupt user or execute -> learn from feedback
```

The important engineering fact: many systems collapse "should I intervene?" and "what task should I propose?" into the same LLM call or a learned reward model. That means the trigger predicate is often not a fixed trusted rule; it is inferred from ambient context.

This supports our security framing: if proactive utility comes from learned judgment over ambient evidence, then IPI-style defenses that require a trusted fixed query/control flow do not directly solve the trigger boundary.

## Common Architecture

### 1. Context Collection

Observed sources across papers/systems:

- desktop activity: active window, browser URL/title, VSCode events, search queries
- app data: email, calendar, Slack/IM, documents, GitHub issues, files
- mobile/GUI state: screenshots, accessibility tree, app notifications
- wearable/AR: egocentric video, audio, location, gaze/activity cues
- long-term memory: user profile, preferences, past accepted/rejected interventions

Engineering pattern:

- Polling loop, cron, or event listener.
- Context is often converted into short natural-language event summaries.
- Provenance is sometimes weak: "the user searches Google..." or "an email from John..." rather than a structured source/trust model.

Security implication:

- Attacks can target raw event sources, summarization, event ordering, event volume, or provenance fields.

### 2. State Tracking / Summarization

Many systems do not feed raw context directly. They maintain:

- recent event history
- user activity summary
- task state
- user profile or memory
- current app/page state

Security implication:

- An attacker can poison not only the current event but the state summary that future triggers depend on.
- Suppression/flooding can work at the summarization layer, not just the raw event layer.

### 3. Trigger / Help-Needed Decision

Common implementations:

- LLM prompt: "Analyze recent events and propose a task if the user needs help."
- learned classifier or reward model: accept/reject whether a proposed task is useful.
- heuristic trigger: rules over calendar time, unread emails, notifications.
- hybrid: rules decide when to wake LLM; LLM decides task and wording.

Security implication:

- Pure rules are easier to secure but less flexible.
- LLM/reward-model triggers preserve proactive judgment but expose task-formation attacks.
- Hybrid systems create two targets: rule wake-up and LLM task inference.

### 4. Candidate Task Generation

Typical output:

- no action / no help needed
- candidate task list
- clarification question
- notification/interruption
- plan or draft
- tool-call proposal

In ProactiveAgent, the agent prompt asks it to analyze history events and provide a task if it thinks the user needs help. This directly merges trigger detection and task generation.

Security implication:

- False task formation is a first-class failure mode, not just bad execution.

### 5. Filtering / Reward / Ranking

Common implementations:

- reward model trained from accept/reject annotations
- LLM judge
- threshold on confidence/helpfulness
- learned policy optimized for proactive F1/precision/recall

Security implication:

- Reward models may learn the same attackable salience cues as the generator.
- Filters can reduce false alarms but may also miss subtle needs.
- Attackers can target the filter, not just the generator.

### 6. User Interaction

Common patterns:

- toast/notification
- inbox item
- ask user a question
- propose draft/action
- wait for accept/reject/ignore
- human-in-the-loop approval for high-risk actions

ProactiveAgent uses desktop toasts; users can accept, reject, or ignore. Ignoring changes future proposal behavior.

Engineering ambient-agent systems such as LangGraph-style agents often use interrupts: the agent runs in the background, then asks the user to approve, answer, or review before continuing.

Security implication:

- Confirmation reduces high-impact harm, but false triggers still consume attention.
- Flooding can create confirmation fatigue or exhaust intervention budgets.
- "Ignore" feedback can be manipulated indirectly by flooding the user.

### 7. Execution / Tool Use

Possible action levels:

- notify only
- ask a question
- draft response
- read/search/fetch context
- write memory
- send message / edit file / accept invite / book order

Security implication:

- The same false trigger has different severity depending on action commitment.
- A defense can gate high-risk tools while still failing at false notifications or memory writes.

## Systems and Benchmarks

### ProactiveAgent / ProactiveBench

Implementation details observed:

- Uses ActivityWatch to collect desktop/browser/VSCode traces.
- PC environment polls activity roughly every 15 seconds.
- Observations are emitted to an event channel.
- Agent listens to observations and prompts an LLM to analyze history events and provide a task if the user needs help.
- Reward model evaluates candidate tasks against human accept/reject labels.
- Desktop toast is used for proactive proposals; user can accept, reject, or ignore.

Data:

- coding, writing, daily-life scenarios
- event summaries with timestamps
- labels like Missed-Need, Non-Response, Correct-Detection, False-Alarm
- released reward data contains `obs`, `pred_task`, `valid`, `help_needed`, `annotation`, `category`

Use for us:

- Strong pilot substrate for task-formation perturbations.
- Weak final substrate for metadata-only claims because events are natural-language summaries, not raw structured provenance.

### ProAgentBench

Positioning:

- Real user sessions and long context.
- Focuses on timing prediction and assist content generation.

Use for us:

- Important related work for realism and long-horizon context.
- If data/code are accessible, useful for suppression/flooding and missed-need analysis.

### Pi-Bench

Positioning:

- Long-horizon personal assistant benchmark.
- Hidden user intents, inter-task dependencies, cross-session continuity.

Use for us:

- Good conceptual match for cross-session task formation and hidden intent.
- More complex than needed for first pilot.

### ProactBench

Positioning:

- Conversational proactivity.
- Trigger points include emergent, critical, and recovery needs.

Use for us:

- Good for dialogue proactivity, but less ideal for ambient event-stream attacks.
- Useful related work, not primary substrate.

### ContextAgent / ProAgent / GOALIE / YETI

Positioning:

- Multimodal/wearable/AR proactive assistance.
- Use sensory context such as video/audio/activity to decide when to intervene.

Use for us:

- Strong evidence that proactive agents are moving beyond text.
- Best future setting for metadata/sensor/context manipulation.
- Harder to reproduce quickly.

### CodingGenie / ProCodeBench

Positioning:

- Proactive coding assistance in IDEs.
- Context from code, task description, editor actions, and history.

Use for us:

- Good domain if we want concrete file/GitHub/IDE event attacks.
- But adversarial control is narrower unless issues, dependencies, docs, or external code comments enter the context.

### Ambient Agents in Engineering Practice

Patterns from public engineering docs/blogs:

- background process watches event streams
- agent stores long-running state/memory
- agent creates an interrupt or inbox item when it needs user input
- human-in-the-loop for risky actions
- cron/polling jobs and event-driven triggers are common
- approval/review UI is treated as central product surface

Use for us:

- Confirms the architecture is not just academic.
- Suggests evaluation should include attention burden, interrupts, approval fatigue, and action commitment.

## Implementation Patterns Relevant to Security

### Pattern A: One-Shot LLM Trigger

```text
recent events -> LLM -> candidate task or no task
```

Pros:

- flexible, easy to implement
- strong proactive behavior

Cons:

- hardest to secure
- no clean trusted trigger predicate
- vulnerable to event wording, salience, ordering, and correlation

Likely in early prototypes and benchmarks.

### Pattern B: Candidate Generator + Reward Filter

```text
recent events -> LLM candidate tasks -> reward model accept/reject
```

Pros:

- reduces false alarms
- supports precision/recall evaluation

Cons:

- reward model may share same vulnerable cues
- attacks can target either generator or filter
- filtering does not equal security

ProactiveAgent is close to this pattern.

### Pattern C: Rule Wake-Up + LLM Judgment

```text
rules detect possible situation -> LLM decides task/content
```

Pros:

- cheaper and safer than always-on LLM
- easier to reason about wake-up

Cons:

- attackers can target the rule trigger
- may miss subtle proactive needs
- rule expansion becomes brittle

This is probably common in products.

### Pattern D: LLM Trigger + Human Approval

```text
LLM detects need -> asks user -> executes only after approval
```

Pros:

- reduces high-impact harm
- practical product design

Cons:

- false activations still harm attention
- confirmation fatigue
- does not solve missed/suppressed activations

### Pattern E: Static Trigger / Cron Agent

```text
fixed schedule or fixed condition -> run agent
```

Pros:

- easiest to secure
- compatible with CaMeL-like trusted control flow

Cons:

- least "proactive" in the interesting sense
- becomes reminder automation rather than judgment-based assistant

## Security-Relevant Design Questions

For each proactive system, record:

- What context sources does it observe?
- Are sources structured with provenance, or summarized into text?
- What decides whether to intervene: rule, LLM, classifier, reward model, or hybrid?
- Is trigger detection separate from task generation?
- Does it distinguish low-trust ambient evidence from user-authored intent?
- Is there a user confirmation path?
- Can it write memory?
- Can it call external tools?
- Does it have an intervention budget/rate limit?
- Does feedback from accept/reject/ignore update future behavior?

## Implications for Our Work

1. We should not assume a single architecture. The paper should evaluate at least two:
   - one-shot LLM trigger
   - candidate generator + reward filter
   - optionally rule wake-up + LLM judgment

2. ProactiveBench is useful for an initial event-text setting, but final security claims need structured event metadata.

3. The cleanest attack target is the trigger/help-needed decision, not the final tool execution.

4. A realistic defense story needs both:
   - execution-layer IPI defenses
   - activation-layer defenses such as provenance, diversity, confirmation, and intervention budgets

5. The strongest paper figure may be a utility/security frontier:

```text
more judgment-based proactivity -> higher useful recall, higher task-formation attack surface
more fixed trusted triggers -> lower attack surface, lower proactive recall
```

6. We should design attacks according to implementation stage:

| Stage | Attack examples |
|---|---|
| context collection | fake calendar invite, crafted issue label, noisy notification stream |
| summarization | event wording manipulation, salient detail omission |
| trigger | metadata-only false trigger, cross-app correlation |
| reward filter | make false task look acceptable/helpful |
| user interaction | notification flooding, confirmation fatigue |
| memory | false preference or standing task write |
| execution | ordinary IPI/tool misuse |

The paper should clearly avoid making execution-stage ordinary IPI its novelty.
