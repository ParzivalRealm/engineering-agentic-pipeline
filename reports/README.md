# reports/ — validation outputs (one per run, never overwritten)

| Files | What they are |
|---|---|
| `para_validation_v1_*.csv` | The baseline: the first validation, built from the `.dpl` export of 8 October 2026. Summary, Defects (D1-D10), Decisions (X1-X4), and every instance DPE with its status. |

This baseline is the known answer for rung 1: a run through para-read must
reproduce D1 (43 transmitters with direction Undefined), D3 (35 valve
timeouts with no connection) and D4 (3 live XXX_DB placeholders). A
difference is information, not something to fix silently.

New runs add new files with a date in the name. Nothing in this folder is
ever edited by hand or overwritten.
