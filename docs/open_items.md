# Open items - how to use the register

`open_items.csv` is the one list of everything still open on SafeStack. Other
documents (hand-off, validation report, handovers, test specification) are
where an item came *from*; this register is where it is *tracked*. When an
item closes, change its Status to Done and say how in the commit message.

## Columns

| Column | Meaning |
|---|---|
| Lane | Model (cross table), Build (tools), Run (PARA defects), PLC |
| Status | Ready - can be done now. Needs decision - only Santos can answer. Needs info - a fact from the PLC, a person or the customer. Blocked - waits on Depends on. Confirm status - may already be fixed; check. Optional. Done. |
| Owner | Santos, Executor (Claude Code), Planner (Claude in chat), Team |
| Done when | The evidence that closes it - a check result, a report, a commit. "Fixed" without evidence is not done. |

## The flow

Each lane has its own loop, and they unblock each other in this order:

1. **Model lane, Ready items.** Edit the workbook, export, run the link
   check, commit. CT-01, CT-03, CT-04 and CT-06 clear four of the six
   remaining issues: the known answer is 6 -> 2, leaving SequenceInProgress
   (CT-02) and the derived alarm chain (CT-05).
2. **Decisions, in one sitting.** Answer every Needs decision and Needs info
   item, as User Replies, the same way as the hand-off. Answers become rules
   or rows; record each in the commit message.
3. **Build lane.** P1: paste hand-off rev 2 section 8 into Claude Code. Its
   report unblocks OI-T02, OI-T03 and OI-T09.
4. **Run lane.** After P1 and the validator rewrite: rung 1 (reproduce
   validation v1), then P2, then D4 on PX9 (rung 2), then D1 across all 43
   (rung 3).
5. **In parallel, any time:** the CT-02 trace (read-only) and the three PLC
   status checks.

## Asking the planner

The register is the planner's input. A safe first run task:

    Run task: use the planner agent. Read docs/open_items.csv and the latest
    files in reports/. Propose today's order of work, Ready items first, and
    list the questions only Santos can answer. Change nothing.

## ID prefixes

| Prefix | Means | Came from |
|---|---|---|
| CT- | Cross table (the PLC-HMI workbook) | Link check; model README |
| D1-D10 | Defects: unambiguous fixes | PARA validation v1 |
| X1-X4 | Decisions a person must settle | PARA validation v1 |
| OI-T | Open items, tooling | Planner-executor hand-off |
| P1, P2 | Build phases: para-read, para-fix | Planner-executor hand-off |
| AL | Allowlist generation | Planner-executor hand-off |
| CAP- | Capability: a new reader the system needs | Chat design notes |
| OI-01, OI-16 | PLC open items | PLC handover rev 3 |
| TS-8.x | Notes before first execution | Test specification, section 8 |

## Testing ladder

Each rung proves one capability against answers already known. Climb in order.

| Rung | What it proves | Register items |
|---|---|---|
| 1 Reproduce | para-read and the validator re-find validation v1's defects, read-only (D1: 43, D3: 35, D4: 3) | P1, OI-T02 |
| 2 Fix one | para-fix applies one approved fix; re-validation confirms it | P2, AL, D4 (PX9 only) |
| 3 Fix a class | the same fix across a whole defect class | D1 (all 43), then D2, D3 |
| 4 Generate | the system creates missing configuration, not just repairs it | D9 |
| 5 Cross-layer | panel writes checked against PARA directions | CT-02, CAP-1 |
| 6 From scratch | a new element or station built from its PLC code | future |