# exports/ — facts (what is true now)

Snapshots of the live configuration. Each file is evidence from one moment;
never edited.

| File | What it is |
|---|---|
| `regularExportAllDpTypes.dpl` | ASCII Manager regular export, 8 October 2026: datapoints, alert values, distribution info, DP functions, peripheral addresses, archive config. Source of the baseline validation. |

Once para-read exists (Phase 1), its CSV exports become the normal facts
source. The `.dpl` stays as the baseline the first para-read run is compared
against.
