---
title: "The closed-world rule — what it is, where it comes from, when to use it"
subtitle: "Learning note · 13 October 2026 · SafeStack agents"
---

# 1. The short version

> **Closed-world rule:** the agent may only treat as true what it can find in
> a defined, finite set of sources. Anything not in those sources is
> *unknown*, and the agent says so instead of filling the gap.

It is the difference between an engineer who says "the drawing doesn't show
that, let me check" and one who says "it's probably 4–20 mA, they usually are."
The second engineer is often right. That is exactly what makes them dangerous.

# 2. Where the idea comes from

## 2.1 How the name got into this repo

Be clear about provenance, since you asked:

- In this session, the phrase *closed-world rule* came from **you**: it is in
  the folder structure you pasted (`CLAUDE.md — language, closed-world rule,
  safety policy`). I can't see the earlier chat with the planner where that
  structure was drafted, so I can't tell you who first proposed the term there.
- I don't have a personal memory of other projects to draw on. What I
  "know" about the concept comes from training on public material: database
  theory, logic programming, knowledge-representation literature, and the
  more recent writing on grounding LLM agents. Everything in section 2.2 is
  standard, citable background you can verify. Section 3 onwards is my
  application of it to your situation.

## 2.2 The original concept: the Closed-World Assumption (CWA)

The term comes from logic and databases, decades before LLMs.

**Closed-World Assumption (CWA).** *If a fact is not stated in the knowledge
base, it is false.* Formalised by **Raymond Reiter, "On Closed World Data
Bases" (1978)**, in *Logic and Data Bases*, eds. Gallaire & Minker.

You use CWA every day without naming it:

- A SQL query for flights from Houston to Madrid returns no rows → you
  conclude there *is* no such flight. Absence of a row means false.
- A WinCC OA `dpNames()` call that matches nothing returns `[]` (F-04) → you
  conclude no such datapoint exists *on that system*.

Reiter's paper names two companion assumptions that are worth knowing,
because they show up in your project too:

- **Unique Names Assumption** — two different names mean two different
  things. (`System1:_Safestack` and `System2:_Safestack` are *different*
  connections. That is DEC-06.)
- **Domain Closure Assumption** — the only things that exist are the ones
  named in the knowledge base. (The only dpTypes in scope are the five you
  export.)

**Negation as failure.** The logic-programming version: in Prolog, `\+ X`
succeeds if `X` cannot be proven. See **Keith Clark, "Negation as Failure"
(1978)**, same book.

**The opposite: the Open-World Assumption (OWA).** *If a fact is not stated,
it is unknown.* This is the stance of the Semantic Web (RDF, OWL): the web is
never complete, so missing data proves nothing.

| | Closed world | Open world |
|---|---|---|
| Fact not in the sources | False | Unknown |
| Good when | The source is complete by construction (a DB, a register, an export) | The source is a partial view of a bigger reality |
| Typical home | SQL, Prolog, configuration databases | Semantic Web, OWL ontologies, the internet |
| Failure mode | Wrongly concluding "no" because data is missing | Never being able to conclude "no" |

## 2.3 How it changed for LLM agents

An LLM brings a third world that classical systems didn't have: **its own
training**. It "knows" a great deal about WinCC OA, S7 drivers and typical
configurations, and it will happily use that knowledge to fill gaps,
fluently and confidently. That gap-filling is what people call
*hallucination* when it's wrong, and *helpfulness* when it's right. The model
cannot reliably tell which is which.

So in agent work, "closed-world" has come to mean something slightly
different from Reiter's CWA:

> **Closed world of sources, open world of conclusions.**
> The *sources* are a closed, named list (only these count as evidence).
> But a fact *missing* from them is reported as **unknown**, not false.

That is the version in `CLAUDE.md`. It closes the door on training knowledge
and guesses, while refusing the classical CWA's risky step of turning
"missing" into "no". Section 3.3 shows why that matters for you.

# 3. How it applies to SafeStack

## 3.1 Why this project needs it

Four things about your situation make guessing especially costly:

1. **The domain is full of plausible defaults.** Direction codes, poll
   groups, transformation types — an LLM has seen thousands of WinCC OA
   configurations and will "know" what is typical. Your project is not
   typical; it is *yours*. `_datatype` 0 on 43 × 7 DPEs (F-13) is the perfect
   example: a model could confidently explain what 0 means. Nobody has
   checked yet (OI-T09).
2. **The tools are writing to a real process** (Phase 2). A confident wrong
   belief that becomes a `para-fix` is a field problem, not a typo.
3. **There are several sources that disagree in time.** The `.dpl` is a
   snapshot, the live read is now, the model is the intent. The rule forces
   every claim to say which one it came from (R-05).
4. **The installed software already contradicted expectations.** F-07 (extra
   direction constants), F-09 (`get-value` can't read config attributes) —
   the executor found these only because it read the actual code instead of
   assuming the documentation was complete.

## 3.2 What the closed set is

Each question has exactly one place it may be answered from:

| Question | Source | Kind of world |
|---|---|---|
| What should it be? | `model/` | Intent, owned by people |
| What is it now? | live `para-read` | Truth, right now |
| What was it? | `exports/*.dpl` | Truth, at a date |
| What did we find? | `reports/` | Derived, at a date |
| Why? | `docs/` | Decisions and history |

Your hand-off already practises this discipline: **Facts** (verified, cited),
**Decisions** (agreed), **Assumptions** (believed, with a status), **Open
items** (unknown, with an owner). That classification *is* the closed-world
rule written as a document format. Only rows in the Facts table are allowed to
be treated as true.

## 3.3 The trap: "no rule" is not "pass"

This is where classical CWA would hurt you, and why the repo uses three
outcomes instead of two.

OI-T08 says the PARA rules do not yet cover `lowlevel`, per-DPE poll-group
choice, or the driver number. A validator built on pure CWA would reason:
*no rule says this is wrong → it is not wrong → pass*. The report would come
back green while, for example, `FaultSubValue` sits on `_SLOW` and nobody
decided that is OK.

So every comparison has three outcomes:

- **Pass** — a rule covers it and it holds.
- **Defect** — a rule covers it and it breaks.
- **Not covered / unknown** — no rule, not in the cross table, or the read failed.

OI-T04 (cross-system addresses reported as *decisions*, not defects) is the
same idea applied by hand: the model doesn't say whether that is allowed, so
the honest answer is "a person must decide."

A useful health metric falls out for free: **the size of the "not covered"
bucket is a measure of how incomplete the model is.** Each rule added to
`model/` should make it shrink.

## 3.4 Examples, right and wrong

| Situation | Wrong (open-world guessing) | Right (closed-world) |
|---|---|---|
| `_datatype` is 0 | "0 means default transformation, that's fine." | "0 — meaning unknown, OI-T09 open. Not counted as pass." |
| Direction 14 appears | "That's input spontaneous." (from memory) | Decoded from `constants.js`: `INPUT_SPONT_ON_USE` (DEC-03). |
| Connection `System2:_Safestack` | Strip the prefix, match `_Safestack`, pass. | Keep the prefix; cross-system → decision for Santos (OI-T04). |
| DPE not in the cross table | Skip it silently. | List under "not covered". |
| The live read fails for one DPE | Use the `.dpl` value instead. | Report the error; show the `.dpl` value separately, labelled with its date. |
| Planner wants to know poll-group policy | Propose the "usual" grouping. | "Not in `model/`. Needs a rule from Santos." |

# 4. Using it elsewhere: how to spot the need

## 4.1 Signs you need a closed-world rule

Ask these questions about any agent or automation task. Two or more "yes"
answers and you want the rule.

1. **Is there an authoritative source?** A database, a register, a cross
   table, a spec, a contract, an export. If the truth lives somewhere
   specific, the agent should be tied to it.
2. **Would a plausible guess be hard to tell from a fact?** Domains with
   strong conventions (industrial config, legal, medical, finance, tax codes)
   are the most dangerous, because the guess *looks* right.
3. **Does the output lead to an action?** Writing config, sending a quote,
   placing an order, changing a setpoint. The closer to a write, the more
   you need it.
4. **Is this installation different from the textbook?** Custom types,
   site-specific naming, legacy settings, local decisions.
5. **Will someone audit the result later?** If every claim must be traceable
   to a source, the agent must only make claims it can trace.
6. **Can the sources disagree?** Snapshot vs live, spec vs as-built. You need
   the rule to force every claim to say which source it came from.

## 4.2 When *not* to use it (or loosen it)

- **Brainstorming and design**: you *want* the model's general knowledge.
  "What are common ways to structure poll groups?" is an open-world question.
- **Explaining concepts**: like this document. General knowledge is the point.
- **No authoritative source exists yet**: closing the world on an empty set
  just produces "unknown" for everything. Build the source first.

A practical pattern: allow general knowledge in the **planner** for *ideas*,
labelled as such ("in general, S7 setups often…"), but never as *evidence*. A
general-knowledge idea becomes usable only after it's checked against a
source and moved into Facts or Decisions.

## 4.3 Recipe for applying it to a new use case

1. **List the sources.** Name each file, table, or tool. Write down which
   question each one answers.
2. **Define "missing".** For each source: is it complete (missing = false,
   classical CWA) or partial (missing = unknown)? Usually only very few
   sources are truly complete.
3. **Give "unknown" a home.** A third outcome, an "open items" list, a
   "decisions needed" section. If the output format has no place for
   "unknown", the agent will force it into pass or fail.
4. **Require citations.** Every claim points to its source. A claim with no
   source is either deleted or moved to Assumptions.
5. **Back it with tools, not only words.** Prompts can be ignored; missing
   tools cannot be used. Your planner has no write tools and para-read has no
   write path — that enforces the rule harder than any sentence in `CLAUDE.md`.
6. **Measure the unknowns.** Track the "not covered" count over time. It
   tells you where the source needs work.

# 5. Research kickstart

## 5.1 Terms to search

| Term | What you'll find |
|---|---|
| *Closed-world assumption* / *open-world assumption* | The core definitions and comparisons. |
| *Reiter 1978 "On Closed World Data Bases"* | The founding paper. |
| *Negation as failure* (Clark 1978) | The Prolog version. |
| *Unique names assumption*, *domain closure assumption* | The companion assumptions. |
| *OWL open world assumption* | Why the Semantic Web chose the opposite. |
| *Three-valued logic*, *SQL NULL* | Formal treatment of "unknown" as a third value. |
| *LLM grounding*, *faithfulness*, *attribution* | How to keep model outputs tied to sources. |
| *Retrieval-augmented generation (RAG) hallucination* | Closed-book vs open-book behaviour. |
| *Abstention*, *selective prediction*, *"I don't know"* in LLMs | Teaching models to say "unknown". |
| *Least privilege* (security) | The tool-level half of the rule (section 4.3, step 5). |

## 5.2 Questions worth answering for SafeStack

1. Which of our sources are **complete** (missing = false) and which are
   **partial** (missing = unknown)? Is the cross table meant to list every
   addressed DPE? If yes, "addressed but not in the cross table" becomes a
   defect, not an unknown.
2. Should the validator have a separate state for **"read error"**, distinct
   from "not covered"? (Suggested in `para-validator.md`: yes.)
3. What is the target size of the "not covered" bucket before Phase 2?
4. Should general knowledge be allowed in the planner at all, and if so, how
   is it labelled?
5. Can we enforce the rule mechanically — e.g. the validator refuses to
   output "pass" for any attribute without a rule ID?

# 6. Revision history

| Rev | Date | Author | Change |
|---|---|---|---|
| 1 | 13 Oct 2026 | Claude Code, for Santos | First version. |
