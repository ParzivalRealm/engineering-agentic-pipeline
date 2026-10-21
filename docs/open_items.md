# Open items - how to use the register

`open_items.csv` is the one list of everything still open on SafeStack. Other
documents (hand-off, validation report, handovers, test specification) are
where an item came *from*; this register is where it is *tracked*.

An item is Done only when its Evidence column is filled with a pointer to
something in Git. Never delete a closed row: set it to Done and filter it out.

## Columns

| Column | Meaning |
|---|---|
| ID | Unique, never reused. See ID prefixes below. |
| Lane | Model (cross table), Build (tools), Run (PARA defects), PLC |
| Title | What is open, in one line |
| Status | Ready - can be done now. Needs decision - only Santos can answer. Needs info - a fact from the PLC, a person or the customer. Blocked - waits on Depends on. Confirm status - may already be fixed; check. Optional. Done. |
| Owner | Santos. Executor - Claude Code, as a build or run task. Planner - Claude in chat, for design work such as the validator and the allowlist. Team. (The planner agent in Claude Code proposes but owns no items.) |
| Next action | The concrete next step |
| Depends on | Items that must be Done first |
| Source | Where the item came from |
| Done when | The criterion that closes it, written in advance: a check result, a report, a commit. "Fixed" without evidence is not done. |
| Resolution | What was decided or done, in one line. When it creates follow-up work, the follow-up gets its own row and the Resolution points to it ("Fixed through D11"). |
| Evidence | Pointer to the proof in Git: a commit hash or a report file. Required before Status is Done. |

## ID prefixes

| Prefix | Means | Came from |
|---|---|---|
| CT- | Cross table (the PLC-HMI workbook) | Link check; model README |
| D | Defects: unambiguous fixes | PARA validation v1, and decisions that became rules (D11 from X3) |
| X | Decisions a person must settle | PARA validation v1 |
| OI-T | Open items, tooling | Planner-executor hand-off |
| P1, P2 | Build phases: para-read, para-fix | Planner-executor hand-off |
| AL | Allowlist generation | Planner-executor hand-off |
| CAP- | Capability: a new reader the system needs | Chat design notes |
| OI-01, OI-16 | PLC open items | PLC handover rev 3 |
| TS-8.x | Notes before first execution | Test specification, section 8 |

New rows take the next free number in their prefix: D11, then D12; CT-17;
and so on.

## The flow

Each lane has its own loop, and they unblock each other in this order:

1. **Model lane, Ready items.** Edit the workbook, export, run the link
   check, commit. CT-01, CT-03, CT-04 and CT-06 clear four of the six
   remaining issues: the known answer is 6 -> 2, leaving SequenceInProgress
   (CT-02) and the derived alarm chain (CT-05).
2. **Decisions, in one sitting.** Answer every Needs decision and Needs info
   item in its Resolution column. A decision that changes a rule usually
   turns a disagreement into a defect: add that defect as a new row and point
   to it (X3 -> D11).
3. **Build lane.** P1: paste hand-off rev 2 section 8 into a normal Claude
   Code session as a build task. Its report unblocks OI-T02, OI-T03 and
   OI-T09.
4. **Run lane.** After P1 and the validator rewrite: rung 1 (reproduce
   validation v1), then D8, then P2, then D4 on PX9 (rung 2), then D1 across
   all 43 (rung 3).
5. **In parallel, any time:** the CT-02 trace (read-only) and the three PLC
   status checks.

## The knowledge loop

Santos is the custodian: agents propose, Santos approves and edits.

1. Decide and edit - the register, the workbook, the rules.
2. Commit, with a message summarising the decisions.
3. Ask the planner agent to review (below). It proposes; it changes nothing.
4. Apply what you agree with, and commit again ("Register: apply planner
   review of <date>").
5. Hand approved work to whoever acts: build tasks to a normal Claude Code
   session, workbook edits to Santos.

## Asking the planner

Start it from the repo root, so it finds `.claude/agents/`:

    cd safestack-agents
    claude --agent planner

Order of work:

    Run task. Read docs/open_items.csv, docs/open_items.md and the newest
    files in reports/. Then propose today's order of work:
    1. Ready items first, grouped by lane, with the reason for the order.
    2. Which items unblock the most others - follow the "Depends on" column.
    3. The questions only Santos can answer, as a numbered list, each with
       the item IDs its answer unblocks.
    Cite item IDs for every claim. If something you need is not in those
    files, say it is unknown rather than guessing. Change nothing.

Review after updating the register:

    Run task. I have updated docs/open_items.csv with resolutions and new
    items. Read it together with docs/open_items.md, the newest files in
    reports/, and git log for the last 10 commits. Then:
    1. Consistency: list every item marked Done without Evidence, every
       Evidence that points to something not in Git, and every Resolution
       that implies follow-up work with no matching row.
    2. Unblocked: list every item whose Depends on items are now all Done,
       and say it can move to Ready.
    3. New rows: propose rows for the follow-ups found in step 1, in the
       register's own columns, using the next free ID in each prefix.
    4. Next: propose today's order of work, Ready items first.
    Cite item IDs and commit hashes for every claim. Change nothing - I will
    apply the changes myself.

## Testing ladder

Each rung proves one capability against answers already known. Climb in order.

| Rung | What it proves | Register items |
|---|---|---|
| 1 Reproduce | para-read and the validator re-find validation v1's defects, read-only (D1: 43, D3: 35, D4: 3) | P1, OI-T02 |
| 2 Fix one | para-fix applies one approved fix; re-validation confirms it | P2, AL, D4 (PX9 only) |
| 3 Fix a class | the same fix across a whole defect class | D1 (all 43), then D2, D3, D11 |
| 4 Generate | the system creates missing configuration, not just repairs it | D9 |
| 5 Cross-layer | panel writes checked against PARA directions | CT-02, CAP-1 |
| 6 From scratch | a new element or station built from its PLC code | future |