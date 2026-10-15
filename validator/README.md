# validator/ - checks that decide

Scripts here are committed, reviewed and tested against known answers. An
ad-hoc script may inform; only a script in this folder may decide.

| Script | Checks | Known answer |
|---|---|---|
| `link_check.py` | Every PARA MAP and PNL MAP in the cross table resolves | 14 issues on the 14 Oct 2026 workbook; 6 after the four key fixes |

Run from the repo root, after exporting the workbook:

    py scripts\export_model.py
    py validator\link_check.py --expect 6

`--expect N` turns a run into a known-answer test: it passes only on exactly
N issues. Each run writes a new dated report to `reports/` and never
overwrites an old one.
