# Opus 4.8 discussion: IPI boundary for proactive task formation

# Brutal Review

## 1. Is there a contribution, or is it IPI repackaged?

There is a *narrow* contribution, but you are currently overselling it and you're right to be nervous. Let me be precise about what survives.

**What is just IPI:** Any case where ambient data carries content that influences *what the agent does once it has decided to act*. The moment a task exists, you're in AgentDojo/Greshake territory. Concede this hard.

**What is potentially novel:** The *decision to instantiate a task at all* from ambient evidence, when there is no user query and no explicit trigger. IPI literature almost universally assumes a task/query exists and asks "can untrusted data hijack its execution?" Proactive agents add a logically prior gate: "should a task be born?" That gate is itself a control-flow decision driven by untrusted data.

But here's the brutal part: **a skeptic can collapse this immediately** by saying the standing instruction *is* the trusted query, and "decide whether to act" is just the first control-flow step of that query. Under that framing, your task-formation gate is literally the first tool call, and contaminating it is textbook IPI. You need a reason that framing is *wrong or insufficient*, not just unappealing. See §3 and §5 — that's where you live or die.

## 2. Framing that survives a skeptic

Drop "Activation Hijacking / Intent Forgery / Task-Formation Attacks." These are marketing names that invite the "this is just IPI with a thesaurus" rejection. Reviewers smell branding.

**Recommended framing:** *Control-flow bootstrapping under ambient triggers.* Position it explicitly as an **IPI subproblem**, not a disjoint phenomenon. Specifically:

> "Existing execution-layer defenses (CaMeL, Instruction Hierarchy) presuppose a trusted query that fixes the intended control flow. Proactive agents have no such fixed control flow; the trigger condition itself is a function of untrusted ambient state. We study whether existing defenses' core assumption — that trusted intent can be separated from untrusted data — even *type-checks* when the trigger is the thing being defended."

Calling it an IPI subproblem is your safest move. It disarms the "repackaging" attack by conceding the genus and claiming a specific species. Reviewers reward honest scoping far more than grand claims.

**Stop calling it "intent forgery."** Forging intent implies the attacker injects a fake instruction — that's IPI. Your interesting case is *absence/correlation/metadata*, where no instruction is injected at all.

## 3. Strongest formal distinction / what to drop

**Drop:** "Proactive agents use untrusted data to determine control flow." Every IPI attack does this. This is not a distinction; it's the definition of IPI. If you lead with this you will be desk-rejected in spirit.

**Strongest real distinction — make it formal:**

In standard IPI, the trusted policy specifies a *deterministic intended control flow* `f(query)`, and the security property is: untrusted data `d` should not change `f`. CaMeL works precisely because `f` is derivable from the trusted query *independently of `d`*.

In proactive agents, the trigger predicate is `g(ambient_state)` where `ambient_state` is *definitionally* untrusted/weakly-trusted. There is **no `d`-independent specification of `g`**. The trusted instruction is "act when useful," and "useful" is only computable over the untrusted data. So the separation CaMeL relies on — trusted control flow vs. untrusted data — is **not merely violated, it is ill-defined**: the control-flow predicate's *domain is the untrusted data*.

That's your one genuinely sharp claim: **IPI defenses assume control flow is specifiable over trusted inputs; proactive triggering is a function whose domain is untrusted inputs, so the trusted/untrusted partition does not exist at the decision boundary.**

If you can formalize that — show that no information-flow partition exists that both (a) keeps the trigger functional and (b) keeps untrusted data out of the control decision — you have a paper. That is an impossibility-flavored result, not a benchmark.

## 4. Experiment that would convince me

A benchmark where you run IPI on proactive agents and report attack success rates would **not** convince me. That's "IPI in a new setting" and a skeptic is right to yawn.

What would convince me:

**Demonstrate that a defense which provably stops IPI in the fixed-query setting fails or is inapplicable in the proactive setting, for a structural reason, not a tuning reason.** Concretely:

- Take CaMeL (or a faithful reimplementation). Show that on AgentDojo-style fixed-query tasks it neutralizes the attack.
- Construct proactive tasks where the *only* attacker input is **metadata/correlation/absence** — no injectable string anywhere CaMeL would classify as data-carrying-instructions.
- Show CaMeL is *forced* to either (a) gate triggering on untrusted ambient state (and thus be exploitable) or (b) refuse to trigger at all (and thus destroy proactive utility). A clean utility/security frontier showing this is a *forced* tradeoff, not a config choice, is the result.

The key empirical object is the **Pareto frontier of proactivity vs. trigger-robustness**, and a demonstration that IPI defenses don't move that frontier because they don't address triggering. If the frontier collapses to "you can have a safe proactive agent or a useful one but not both," that's a real finding.

## 5. How to handle CaMeL — this is your toughest opponent

Assume a reviewer *is* a CaMeL author. Their move: "Treat the standing proactive instruction as the trusted query. Ambient events are untrusted data. CaMeL extracts the control flow from the standing instruction; untrusted events can populate data values but cannot alter the trigger logic. Solved."

**This works for explicit-command attacks. Concede it fully.** An attacker email saying "you should now book a flight" — CaMeL handles that, because the trigger logic came from the trusted standing instruction, not the email.

**Where CaMeL genuinely struggles, and where you must concentrate:** The standing instruction "act when useful" does not contain enough information to derive a control flow. "Useful" must be *evaluated against ambient state*. So either:
- (a) CaMeL hard-codes the trigger predicate in the trusted instruction (e.g., "act iff calendar event within 1hr") — then it's not really proactive, it's a cron job, and you've defined proactivity out of existence; or
- (b) The trigger predicate consults untrusted ambient state to decide — and now untrusted data *is* in the control-flow decision, violating CaMeL's invariant.

Your paper's spine should be: **CaMeL converts proactive agents into rule-based triggers, and the residual "judgment-based triggering" that makes them proactive is exactly the part CaMeL cannot protect.** Quantify how much proactive utility survives full CaMeL-ization. If it's "agents become glorified cron jobs," that's publishable. If proactive utility survives fine under CaMeL, **your paper is dead** — go check this first, before anything else.

## 6. Which attack families survive

Ranked by how well they resist the "this is just IPI" collapse:

1. **Suppression / absence / flooding — STRONGEST.** This is your best material because there is *no injected instruction*. The attacker manipulates the *base rate of triggering* by removing or burying signal. IPI defenses have literally nothing to say about "the attacker prevented a task from forming" or "the attacker raised noise so the trigger threshold was never crossed." There is no malicious string to spotlight, no instruction to subordinate. **Lead with this.**

2. **Metadata-only — STRONG.** Trigger driven by timestamps, sender frequency, geolocation, presence/absence — fields that defenses treat as data, not as instruction-bearing. Survives well because the channel isn't "natural language commands."

3. **Cross-app correlation — MEDIUM-STRONG, but hard to argue cleanly.** The novelty is that no single input is malicious; the *conjunction* triggers. A skeptic will say "compositional IPI exists." True, but the *no-single-malicious-source* property is a real evaluation gap. Defendable if framed as emergent triggering.

4. **Memory/preference contamination — WEAKEST / DROP or separate.** This is just persistent IPI / poisoning. There's an existing literature (memory poisoning in agents). A skeptic crushes this instantly. Cut it or relegate it to a "known and adjacent" note.

## 7. Skeptical reviewer argument + honest rebuttal

**Reviewer:** "A proactive agent has a standing trusted instruction. Ambient events are untrusted data. An attacker influencing whether the agent acts is untrusted data influencing execution of a trusted instruction. That is the definition of indirect prompt injection. The 'proactive setting' is a deployment detail, not a new threat model. CaMeL or instruction-hierarchy approaches apply directly: trusted standing instruction over untrusted ambient data. Reject — incremental."

**Honest rebuttal:** "We concede the genus is IPI and that command-style ambient injection is solved by existing defenses; we explicitly exclude those cases. Our contribution is the *triggering decision* in agents with no fixed control flow. For such agents the trigger predicate is a function whose domain is the untrusted ambient state, so the trusted-control-flow/untrusted-data partition that CaMeL and instruction hierarchy require is not violated but *undefined*. We demonstrate empirically that applying CaMeL forces proactive agents into static rule-based triggers, eliminating the judgment-based proactivity that defines them, and we exhibit an attack class — suppression and absence-based manipulation — that contains no injected instruction and is therefore outside the scope of all spotlighting/hierarchy/dataflow defenses. The contribution is a structural impossibility at the trigger boundary, not a new benchmark."

That rebuttal is winnable **only if §5 check and §4 experiment come out the way you hope.** If they don't, the reviewer is correct.

## 8. Bottom line: REFRAME (and pre-condition on one check)

Do not abandon. Do not pursue as currently framed.

**Reframe** as: *an IPI subproblem at the control-flow-bootstrapping boundary, where the novel and defense-resistant core is absence/suppression-based trigger manipulation, and the central claim is that execution-layer dataflow defenses are structurally inapplicable to the triggering decision.*

**Gating condition before you invest:** Implement CaMeL on a proactive task suite and measure whether full CaMeL-ization destroys proactive utility. 
- If yes (agents become cron jobs) → you have a real paper; pursue hard.
- If no (CaMeL handles proactive triggering fine) → abandon; it was IPI repackaged after all.

Stop saying "intent forgery / activation hijacking." Stop claiming disjointness from IPI. Lead with suppression/absence attacks and the ill-defined-partition argument. Everything else is conceded ground.
