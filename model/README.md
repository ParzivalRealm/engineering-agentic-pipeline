# model/ — knowledge (what should be true)

Owned by people. Agents read it; agents never edit it. A change here is a
design decision and should be recorded in the hand-off document.

| Files | What they are | Source |
|---|---|---|
| `para_rules_Elements.csv` | The 16 controlled elements and the PLC blocks, solenoids and transmitters that belong to each. The entity table that joins things whose names share no common token. | PARA Rules v1 |
| `para_rules_TypeRules.csv` | Per datapoint type: naming rule, expected count, and per element the PLC address rule, Rule (Required / Template / Internal), Role and Direction. | PARA Rules v1 |
| `para_rules_Directions.csv` | WinCC OA `_address.._direction` codes and which codes satisfy each Role. | PARA Rules v1 |
| `crosstable_*.csv` | The navigation map: interfaces, PARA maps, panel maps, glossary and change log. One CSV per sheet, exported as-is. | Cross table v2, Santos's latest edit (14 October 2026) |

Placeholders in address rules: `{DB}` is the PLC instance DB, `{STRUCT}` is
the element's DB84 struct. The validator resolves them from Elements; nothing
downstream ever sees a placeholder.

Known gaps (see hand-off OI-T08, OI-T09): the rules don't yet cover
`_lowlevel`, poll-group choice per element, the driver number, or the S7+
transformation type (`_datatype`).

## Known link issues in the cross table (14 October 2026)

Found by a link check: every PARA MAP must name a DPE that exists in a PM
sheet, every PNL MAP a sheet, and every panel an interface row points to must
have a shape binding that DPE. Fix these in the source workbook, then
re-export; the CSVs are never edited directly.

Key spelling - the binding exists, the key doesn't join (fixing these four
clears eight issues):
- PNLMAPSSChangeStatePopup, HMI_ACK: `PMConnsSeq.HMI_Ack` -> `PMConnSeq.HMI_Ack`
- PNLMAPSystemStatus, PUSH_BUTTON1: `HMI.WinCC_OA_InitiateDisconnectSeq` -> `PMHMI.WinCC_OA_InitiateDisconnectSeq`
- PNLMAPSystemStatus, PUSH_BUTTON2: `HMI.WinCC_OA_InitiateReconnectSeq` -> `PMHMI.WinCC_OA_InitiateReconnectSeq`
- PNLMAPSystemStatus, TABLE1: `<ConnSeqDPT>.FaultStep` -> `PMConnSeq.FaultStep`

Missing or indirect bindings:
- ManualMode points to PNLMAPSystemStatus, but no shape there binds it.
- SequenceInProgress is bound to no panel; the pop-up may consume it through
  the panel variable `g_iSeqInProgress` - not yet recorded.
- Alarm.Alarms reaches the analog faceplate indirectly: DP functions unpack it
  into `Alarm.*`, and the faceplate binds `Alarm.*`. The map has no way yet to
  say "derived".
- Config.FaultSubValue: the faceplate row binds only FaultSubValueEnable
  ("checkbox, PANEL_REF4").
- Lockout and Permissive point to PNLMAP_VALVESV, but SafeStack doesn't use
  that faceplate.

Content to confirm:
- Interface map, Estop.Pumps: its PARA MAP is `PMHMI.Estop.Valves` (copy of the
  row above), PMHMI has no Estop.Pumps element, and the PLC change of
  September 2026 removed Estop.Pumps from DB84.
- PNLMAPEstopBtn: Event reads "Subscribe" and Action "Set"; the note still
  says the row is a placeholder.
- PNLMAPSSChangeStatePopup, HMI_ACK: Action "Subscribe, Clicked" - Clicked is
  an event.
- PMHMI: a stray cell "PMHMI.Estop.Valves" outside the table (column 11).
- Location column exists on two of seven PNL sheets.
- Panel variables (`g_bActionRequested`, `g_iSeqInProgress`) are marked "Not on
  Para" only in Notes; a tool cannot rely on note text.

None of this affects the PARA rules or validation v1: the validator reads
`para_rules_*.csv`, not the cross table.
