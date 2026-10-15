---
title: "SafeStack — PARA MCP tools: planner–executor hand-off"
subtitle: "Revision 2 · 13 October 2026 · Phase 0 closed, Phase 1 approved with changes"
---

# 1. Status

| Phase | State |
|------------------|------------------------------------------|
| 0 — Investigate and plan | Done. No files written. |
| 1 — para-read | Approved with the changes in section 8. Ready to start. |
| 2 — para-fix | Not started. Waits for "go Phase 2". |

**Roles.** Santos approves plans, restarts the JavaScript Manager and owns every decision. The planner (Claude, in chat) designs, reviews and writes the executor's instructions. The executor (Claude Code, inside the VM) investigates, builds, tests and reports.

**How to read this document.** Facts are verified and no longer up for discussion. Decisions are agreed and binding on the executor. Assumptions are things still believed rather than proven, each with a status. Open items need an owner and an action. Section 8 is what goes to the executor next.

# 2. Facts established in Phase 0

Verified by the executor in the installed code, or against the `.dpl` export.

| ID | Fact | Consequence |
|------|------------------------------------|------------------------|
| F-01 | `tool_loader.js` imports `./tools/<entry>.js` for each `TOOLS` entry and calls its `registerTools(server, context)`. There is no registry or manifest. | A new tool is a folder under `tools/` plus a `TOOLS` entry. The server core is not touched. |
| F-02 | On `npm update`, the postinstall copies `build/` over `mcpServer/`, overwriting files with the same name and deleting nothing. | `tools/para/` survives updates unless the package ever ships its own `tools/para/`. |
| F-03 | Node resolves packages such as `zod` from the importing file's location. | Custom tools must live inside `mcpServer/`. |
| F-04 | `dpNames(pattern, dpType?, ignoreCase?)`: `**` matches all levels; a pattern matching nothing returns `[]` without throwing; matching is level by level. | `*.Alarm.Alarms` matches only three-level names. Use `**` for depth. |
| F-05 | `dpGet(string[])` accepts config attributes such as `X:_address.._direction`. A batch is all-or-nothing: one bad element fails the call with error 9399. | Batched reads need a per-DPE fallback. |
| F-06 | `_address.._type` reads 0 (`DPCONFIG_NONE`) when a DPE has no address, and 16 (`DPCONFIG_PERIPH_ADDR_MAIN`) for an S7+ address. | Read `_type` first. A missing address is a row with `addrType` "none". |
| F-07 | The direction constants are not in the Siemens typings; they are in `mcpServer/types/winccoa/constants.js`. The planner's table matches. The installed constants add 10 and 12 (marked not in use), 14 `INPUT_SPONT_ON_USE`, 15 `IO_SPONT_ON_USE`, and two obsolete flag bits: 32 `INTERNAL` and 64 `LOW_LEVEL_FLAG`. | Decode from the server's constants. Strip the flag bits defensively. |
| F-08 | `winccoa.getPaths()[0]` is the project directory. | The export folder is fixed in code, not set in `.env`. |
| F-09 | `get-value` cannot read config attributes for two reasons: `helpers.js` rejects any name containing `..` (with a misleading "Wildcard '*'" message), and `get-value` appends `:_online.._value` to the name. | The built-in tools cannot do PARA work. Worth reporting upstream (OI-T07). |
| F-10 | The `.dpl` agrees with acceptance tests 1–3. PX9 `Alarm.Alarms`: type 16, `_Safestack`, `_subAnalog`, direction 0, active, `_lowlevel` 1. PX9 `Config.FaultSubValue`: reference `XXX_DB.Retain.HMI.Config.SAV`, poll group `_SLOW`, direction 11. SOL01A `Alarm.TimeoutClose`: no connection, no poll group, direction 4. | Tests 1–3 are pre-verified offline. Phase 1 must reproduce them live. |
| F-11 | `BaseConnection.js` writes all `_address` attributes, including `_active`, together in one `dpSetWait`. | Precedent for the Phase 2 write pattern. |
| F-12 | *Planner, from the `.dpl`.* Every DPE's `_distrib.._driver` is 1, matching the S7+ driver's manager number. | The driver check should pass on every row. A future mismatch would be a silent failure, which is why it is read. |
| F-13 | *Planner, from the `.dpl`.* `_datatype` (the S7+ transformation) is 0 on `Alarm.Alarms` and on `Setpoint.H`, `HH`, `L`, `LL`, `OR` and `UR` for all 43 transmitters. Their siblings use explicit types: 1001 default, 1002, 1012, 1015. | Defect D1 may need the transformation fixed as well as the direction. See OI-T09. |

# 3. Decisions

| ID | Decision | Reason | By |
|------|------------------------------------|------------------------|------------|
| DEC-01 | The tools live in `mcpServer/tools/para/`, and that folder is committed to Git. | F-02, F-03. The source must survive updates and be reviewable. | Executor proposal, Santos approved |
| DEC-02 | Shared code goes in `para_common.js`, the tool in `para_read.js`. Phase 2 reuses `para_common.js`. | para-fix must read before it writes, with the same reader. | Executor proposal, Santos approved |
| DEC-03 | Direction is decoded from the server's `constants.js`, not from a hard-coded table. | F-07 | Executor proposal, Santos approved |
| DEC-04 | Reads run in two batched passes — `_type` first, then the remaining attributes for addressed DPEs. A failing batch is retried one DPE at a time, and failing rows carry an `error` field. | F-05, F-06 | Executor proposal, Santos approved |
| DEC-05 | Every row and the CSV include `lowlevel` and `internal`. | ASM-01. A future PARA rule may need them. | Santos |
| DEC-06 | System prefixes are kept and matched everywhere, never stripped: in DPE names, connections and poll groups. Rows also carry the parsed parts (`system`, `connectionSystem`, `connectionName`, `pollGroupSystem`, `pollGroupName`). | ASM-02. Some projects run several systems; the prefix is meaningful. | Santos |
| DEC-07 | Rows are sorted by DPE before paging. | Pages must be deterministic. | Executor proposal, Santos approved |
| DEC-08 | The only `.env` change in Phase 1 is appending `,para/para_read` to `TOOLS`. | Ground rule 2. | Standing rule |
| DEC-09 | `.env` never enters Git. | It holds the API token. | Planner |
| DEC-10 | Exports are always scoped by `dpType`. Exporting `*.**` with no type is not done. | Without a type, `*.**` sweeps in WinCC OA's internal datapoints. | Planner |

# 4. Assumptions

| ID | Assumption | Status |
|------|------------------------------------|------------------------------|
| ASM-01 | Add `lowlevel` and `internal` columns. | Confirmed by Santos → DEC-05. |
| ASM-02 | Connection and poll group come back with a system prefix (e.g. `System1:_Safestack`); return them raw and ignore the prefix in tests. | Changed by Santos → DEC-06. The prefix is kept *and* matched, not ignored. |
| ASM-03 | `_direction` reads without the 64 flag bit, and low-level comes from the separate `_lowlevel` attribute. | Supported by evidence (F-10): the `.dpl` stores direction 0 and `_lowlevel` 1 separately. Keep the defensive strip. Meaning to be confirmed from the help (OI-T03). |
| ASM-04 | `_distrib.._driver` is read in the same batch as the address; if `_distrib` is missing, the per-DPE fallback handles it. | Accepted. Evidence in F-12. |
| ASM-05 | Test 4 returns 43 rows with masters excluded (44 including `_mp_SSAC_ANALOG`). | Confirmed. |
| ASM-06 | `*.Alarm.Alarms` matches only three-level names. | Accepted. Recorded as F-04; patterns written by the planner use `**`. |
| ASM-07 | The Phase 2 write follows the `BaseConnection.js` pattern (F-11). | Deferred to the Phase 2 investigation. |

**ASM-03 in plain terms.** In PARA, the address panel has a *low level comparison* option. When it is on, the driver itself compares each new value with the previous one and passes on only changes. Older WinCC OA versions stored this as +64 inside the direction code; current versions keep it in its own attribute, `_lowlevel`. Your export already shows the current form, so the executor's assumption holds, and stripping 64 only guards against old configurations. The executor confirms this against the help before anyone relies on it.

**ASM-04 in plain terms.** `_distrib.._driver` comes from the planner's Phase 1 spec — *Behaviour*, second bullet: *"Otherwise read `_reference`, …, and `_distrib.._driver`."* The address says which PLC connection a DPE uses. `_distrib` says which driver process serves it, by manager number; your S7+ driver runs as number 1. If the two disagree, values never arrive even though the address looks perfect — a silent failure the address alone cannot show. Your export has driver 1 everywhere (F-12), so this check should pass.

# 5. Open items

| ID | Item | Owner | When |
|------|------------------------------------------|------------|------------|
| OI-T01 | Acceptance-test expectations include the system prefix. The executor reports the project's system name and compares full values. | Executor | Phase 1 |
| OI-T02 | Switch the validator's input from the `.dpl` to the para-read CSV, and make it system-aware: DPE names and connection values carry prefixes. | Planner | Before the rung 1 diff |
| OI-T03 | Confirm from the WinCC OA help what `_lowlevel` and `_internal` mean, and whether either should become a PARA rule. | Executor researches; Santos decides | Phase 1 report |
| OI-T04 | Decide whether a DPE addressed to a connection on another system is ever valid. Until decided, the validator reports cross-system addresses as decisions, not defects. | Santos | Before validator v2 |
| OI-T05 | Confirm `tools/para/` is committed and `.env` is ignored. | Executor | Phase 1 |
| OI-T06 | Patterns are level-aware (F-04). Planner prompts and the starter `CLAUDE.md` use `**` for depth. | Planner | Starter repo |
| OI-T07 | Report the `get-value` limitation to the server's maintainers. | Santos (optional) | Any time |
| OI-T08 | Rules backlog: the PARA rules do not yet cover `lowlevel`, poll-group choice per DPE (for example `FaultSubValue` on `_SLOW` while siblings use subscription groups), or the driver number. | Planner and Santos | Validator v2 |
| OI-T09 | `_datatype` 0 (F-13). Find out what transformation 0 means to the S7+ driver — treated as default, or invalid — and check live whether those DPEs update. If 0 is invalid, D1 needs two attribute fixes (direction and datatype), and Phase 2's attribute list must include `datatype`. | Executor researches; planner updates rules and allowlist | Phase 1 report |

# 6. Risks and watch list

| ID | Risk | Mitigation |
|------|------------------------------|------------------------------|
| R-01 | A future package version ships its own `tools/para/` and overwrites ours. | Source committed (DEC-01). Check `tools/para/` after every update. |
| R-02 | Many failing batches push reads to one DPE at a time, making exports slow. | Report export duration per type in every run. |
| R-03 | Rows mode returns too much for the model's context. | Limit capped at 500; compact JSON; full data only through export. |
| R-04 | A pattern without a type sweeps in WinCC OA internal datapoints. | DEC-10. |
| R-05 | Tests pass offline (`.dpl`) but the live read differs — for example prefixes or encodings. | Tests always run live through MCP; raw values are reported, not just pass or fail. |

# 7. Acceptance tests — Phase 1

| # | Call | Expected | Offline (.dpl) | Live |
|------|------------------------------|------------------------------------|------------|------------|
| 1 | `PX9_RDP_CONN_LCK_PRESS_DB.Alarm.Alarms` | addrType 16; direction 0 Undefined; connection `_Safestack` on this system; poll group `_subAnalog`; active; lowlevel true | Agrees | Pending |
| 2 | `PX9_RDP_CONN_LCK_PRESS_DB.Config.FaultSubValue` | reference contains `XXX_DB`; active; direction 11; poll group `_SLOW` | Agrees | Pending |
| 3 | `SOL01A_RDP_CONN_LCK_DB.Alarm.TimeoutClose` | direction 4; empty connection; empty poll group | Agrees | Pending |
| 4 | `*.Alarm.Alarms`, dpType `SSAC_ANALOG` | 43 rows, all direction 0 | — | Pending |
| 5 | Export once per type | SSAC_ANALOG 43, SSAC_VALVE_SV 35, CmdGate 17, ConnSeq 16, HMI 1 datapoints; rows and duration per type | — | Pending |

# 8. Next instructions for the executor

```
Phase 0 is approved, with the changes below. Go Phase 1.

Changes to your plan
1. Columns: add lowlevel and internal to every row and to the CSV.
2. System prefixes: never strip them. Keep full names in dpe, connection
   and pollGroup, and add parsed columns: system (of the DPE),
   connectionSystem, connectionName, pollGroupSystem, pollGroupName.
   Tests compare full values. Start your report with the project's own
   system name, read through the winccoa API.
3. Low-level: keep the defensive flag stripping in decodeDirection.
   Research only: from the WinCC OA help for the _address config, explain
   in two sentences each what _lowlevel and _internal mean, and whether
   either should become a PARA rule. Don't change behaviour based on it.
4. Transformation: research only. _datatype is 0 on Alarm.Alarms and on
   Setpoint.H/HH/L/LL/OR/UR of every SSAC_ANALOG datapoint; other DPEs
   use 1001, 1002, 1012 or 1015. Find out what 0 means to the S7PLUS
   driver. Then read the live value and timestamp of
   PX9_RDP_CONN_LCK_PRESS_DB.Setpoint.HH and Setpoint.HHH with get-value
   and report whether each is updating. Change nothing.
5. Export scope: never export "*.**" without a dpType - it would include
   WinCC OA's internal datapoints. Acceptance test 5 is now: export once
   per type (SSAC_ANALOG, SSAC_VALVE_SV, CmdGate, ConnSeq, HMI) and report
   rows, datapoint count and duration per type.
6. CSV: UTF-8, header row, RFC 4180 quoting.
7. Git: commit javascript/mcpServer/tools/para/ only. Before committing,
   confirm .env is ignored and not staged. Report the commit hash.

Unchanged from your plan: para_common.js plus para_read.js; batched reads
with per-DPE fallback; sort before paging; constants from
mcpServer/types/winccoa/constants.js; project directory from getPaths()[0];
the single .env change (append ,para/para_read to TOOLS).

Ground rules still apply: para-read contains no write calls; touch only
the files above; stop and tell me when the JavaScript Manager needs a
restart.

Acceptance tests, through MCP, after my restart
1. "PX9_RDP_CONN_LCK_PRESS_DB.Alarm.Alarms": addrType 16, direction 0
   Undefined, connection _Safestack on this system, pollGroup _subAnalog,
   active true, lowlevel true.
2. "PX9_RDP_CONN_LCK_PRESS_DB.Config.FaultSubValue": reference contains
   "XXX_DB", active true, direction 11, pollGroup _SLOW.
3. "SOL01A_RDP_CONN_LCK_DB.Alarm.TimeoutClose": direction 4, empty
   connection, empty pollGroup.
4. "*.Alarm.Alarms" with dpType "SSAC_ANALOG": 43 rows, all direction 0.
5. Export per type as in change 5: expect 43, 35, 17, 16 and 1 datapoints.
Report each result against its expectation, with the raw values as read.
A mismatch is information - report it, don't fix it silently.

Report at the end: files created or changed, commit hash, test results,
the research for changes 3 and 4, export timings, and every assumption
you made.
```

# 9. Design principles for every change

These apply to everything the executor builds and the planner specifies.

1. **Separate what varies from what stays the same** — what varies becomes an input.
2. **Put each decision where its knowledge already lives** — resolving `{DB}` belongs to the validator, which loads the rules.
3. **Decide once, as early as full information allows** — pass answers downstream, not questions.
4. **Separate by owner and by rate of change** — rules are data owned by people; code is generic.
5. **The more dangerous a part, the less it knows** — para-read has no write path; para-fix has no value parameter.
6. **Make illegal requests impossible to express** — rather than refusing them after the fact.
7. **Design the failure first** — the worst input, and exactly what happens.
8. **Every hand-off is a file with a schema** — export CSV, `allowlist.json`, `audit.jsonl`, and this document.

# 10. Revision history

| Rev | Date | Author | Change |
|------|------------|------------|------------------------------------------|
| 1 | 13 Oct 2026 | Santos | Executor's Phase 0 report, with User Replies on assumptions 1–4. |
| 2 | 13 Oct 2026 | Planner | Categorised into facts, decisions, assumptions, open items and risks. Added F-12, F-13, DEC-09, DEC-10, OI-T09. Issued Phase 1 instructions. |
