# SafeStack agents — project rules

This repo holds the knowledge and agents that check, and later fix, the PARA
(peripheral address) configuration of the SafeStack WinCC OA project.
Every agent working here reads this file first. If an instruction elsewhere
conflicts with this file, this file wins and you say so.

The background for every decision is in `docs/Planner-Executor_Hand_Off_rev2.md`
(the hand-off). IDs such as F-04, DEC-06 or OI-T08 refer to that document.

---

## 1. Language

- Write to Santos in plain English. Short sentences. Define a term the first
  time you use it if it is not in the glossary below.
- Separate what you **know** from what you **believe**. Use the hand-off's
  categories when reporting:
  - **Fact**: verified by a read (live MCP call, `.dpl` export, file in this repo). Cite the source.
  - **Decision**: agreed by Santos. Binding.
  - **Assumption**: believed, not proven. Give it a status.
  - **Open item**: needs an owner and an action.
- Report raw values as read, not only pass or fail (R-05).
- A mismatch is information. Report it; never fix it silently.

### Glossary

| Term | Meaning here |
|---|---|
| DP / DPE | Datapoint / datapoint element, e.g. `PX9_RDP_CONN_LCK_PRESS_DB.Alarm.Alarms`. |
| dpType | Datapoint type, e.g. `SSAC_ANALOG`, `SSAC_VALVE_SV`, `CmdGate`, `ConnSeq`, `HMI`. |
| PARA | The WinCC OA parameterisation of a DPE's peripheral address (`_address` config). |
| System prefix | `System1:` in front of a name. Kept and matched everywhere, never stripped (DEC-06). |
| Cross table | The engineering list of which DPE should be addressed, to what, and how. Lives in `model/`. |
| PARA rules | Rules that say what a correct address looks like. Live in `model/` as CSV. |
| Defect | A DPE whose live PARA breaks a rule. Has an ID (e.g. D1). |
| para-read | MCP tool that reads PARA. Has no write path. |
| para-fix | MCP tool (Phase 2) that corrects one defect from an allowlist. Has no value parameter. |
| `.dpl` | ASCII export of datapoints and configs. Snapshots live in `exports/`. |

---

## 2. Closed-world rule

> Only what is in the sources listed below exists. Anything not found there
> is **unknown**, and you say so. You never fill a gap from general knowledge,
> from memory of other projects, or from what "usually" holds in WinCC OA.

The long explanation, with background and how to apply it elsewhere, is in
`docs/closed-world-rule.md`.

### The closed set of sources

| Question | The only allowed source |
|---|---|
| What *should* the PARA be? | `model/` (cross table + PARA rules CSV) |
| What *is* the PARA, now? | A live `para-read` call through MCP |
| What *was* the PARA? | A `.dpl` snapshot in `exports/` (name the file and date) |
| What did a check find? | A report in `reports/` (name the file) |
| Why is it built this way? | The hand-off and other files in `docs/` |
| How does the check work? | The code in `validator/` |

### Three answers, never two

When you compare a DPE against the model, every result is one of:

1. **Pass**: a rule covers it and the live value satisfies the rule.
2. **Defect**: a rule covers it and the live value breaks the rule.
3. **Not covered / unknown**: no rule covers this attribute, the DPE is not in
   the cross table, or the read failed. **This is not a pass.** List it
   separately so a person can decide (see OI-T04, OI-T08).

### What the rule forbids, concretely

- Inventing a DPE, connection, poll group, direction code or rule that you have
  not read from a source above.
- Decoding a direction or transformation from memory. Directions come from the
  server's `constants.js` (DEC-03). `_datatype` 0 stays "unknown meaning"
  until OI-T09 closes.
- Treating "the model says nothing" as "fine".
- Treating the `.dpl` as live. It is a snapshot; say which one.
- Silently dropping or stripping the system prefix.

If you need something that is not in the closed set, stop and ask Santos for
the file or the read. That is a correct outcome, not a failure.

---

## 3. Safety policy

The project controls a real process. Reads are cheap; writes are not.

### Who may do what

| Actor | May | May not |
|---|---|---|
| Santos | Approve plans, restart the JavaScript Manager, decide every open item, say "go Phase 2" | — |
| `planner` | Read the repo, propose plans and rule changes | Write files, call any MCP tool, run commands |
| `para-validator` | Call read-only MCP tools, run the validator, write a new file in `reports/` | Call `para-fix` or any write tool, edit `model/` or `validator/` |
| `para-executor` | After "go Phase 2": call `para-fix` for **one** approved defect at a time | Batch fixes, fix anything not in the allowlist, choose a value |

### Hard rules

1. **No writes to the WinCC OA project** except through `para-fix`, in Phase 2,
   for a defect Santos has approved. No `dpSet`, no import of a `.dpl`, no
   built-in write tool, ever.
2. **Read before write, with the same reader.** para-fix reads through
   `para_common.js` before it writes (DEC-02).
3. **One defect at a time.** Read, fix, read back, report, then wait.
4. **Exports are always scoped by `dpType`.** Never export `*.**` without a
   type (DEC-10).
5. **Patterns are level-aware.** `*` matches one level, `**` matches any depth
   (F-04). Use `**` when you mean "anywhere below".
6. **`.env` never enters Git and is never printed.** It holds the API token (DEC-09).
7. **Stop and ask** when the JavaScript Manager needs a restart, when a read
   fails in a way you cannot explain, or when a result contradicts the model.
8. **Reports are append-only.** A new run gets a new file in `reports/`
   (`YYYY-MM-DD_HHMM_<scope>.md` / `.csv`). Never overwrite an old report.

---

## 4. Repo layout

```
CLAUDE.md          this file
model/             cross table + PARA rules as CSV        (owned by people)
docs/              hand-offs, test spec, learning notes   (Markdown)
validator/         the validation script                  (code, generic)
exports/           .dpl snapshots and para-read CSVs      (evidence, dated)
reports/           validation outputs, one per run        (append-only)
.claude/agents/    planner, para-validator, para-executor
```

Rules are data owned by people; code is generic (design principle 4). A rule
change is an edit to `model/`, reviewed by Santos — not a change to the validator.
