"""Link check for the cross table: every reference must resolve.

Rules
  1. An interface-map PARA MAP must name a DPE defined in a PM sheet (sheet.DPElement).
  2. An interface-map PNL MAP must name an existing PNL sheet.
  3. If a row names both, that PNL sheet must have a shape binding that same DPE.
  4. An interface-map row with no PNL MAP is reported as not bound.
  5. A PNL row's PARA MAP must name a DPE defined in a PM sheet, unless it is
     empty or marked as not a datapoint (VAR: prefix, or "Not on Para" in Notes).

Reads model/crosstable_*.csv (run scripts/export_model.py first).
Writes reports/link_check_<timestamp>.csv - never overwrites.

Usage:  python validator/link_check.py               exit 0 if no issues
        python validator/link_check.py --expect 14   exit 0 only if exactly 14 (known-answer test)
"""
from pathlib import Path
from datetime import datetime
import argparse
import csv
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "model"
REPORTS = ROOT / "reports"

def load():
    sheets = {}
    for f in sorted(MODEL.glob("crosstable_*.csv")):
        sheets[f.stem.removeprefix("crosstable_")] = pd.read_csv(f, dtype=str).fillna("")
    return sheets

def cell(row, col):
    return str(row.get(col, "")).strip()

def check(sheets):
    im = sheets.get("SafeStackPLCHMIInterfaceMap")
    if im is None:
        raise SystemExit("Interface map CSV not found - run scripts/export_model.py")
    pm = {n: df for n, df in sheets.items() if n.startswith("PM")}
    pnl = {n: df for n, df in sheets.items() if n.startswith("PNLMAP")}
    dpes = {f"{n}.{e.strip()}" for n, df in pm.items() for e in df.get("DPElement", []) if e.strip()}

    issues = []
    for _, r in im.iterrows():
        member, para, panel = cell(r, "Member"), cell(r, "PARA MAP"), cell(r, "PNL MAP")
        if para and para not in dpes:
            issues.append(("Interface map", member, 1, f"PARA MAP '{para}' is not a DPE in any PM sheet"))
        if panel and panel not in pnl:
            issues.append(("Interface map", member, 2, f"PNL MAP '{panel}' is not a sheet"))
        if panel in pnl and para:
            bound = set(pnl[panel].get("PARA MAP", pd.Series(dtype=str)).str.strip())
            if para not in bound:
                issues.append(("Interface map", member, 3, f"points to {panel}, but no shape there binds {para}"))
        if not panel:
            issues.append(("Interface map", member, 4, "not bound to any panel"))
    for name, df in pnl.items():
        for _, r in df.iterrows():
            para = cell(r, "PARA MAP")
            if not para or para.startswith("VAR:") or "Not on Para" in cell(r, "Notes"):
                continue
            if para not in dpes:
                issues.append((name, cell(r, "Shape/Ref"), 5, f"PARA MAP '{para}' is not a DPE in any PM sheet"))
    return issues

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--expect", type=int, help="known-answer test: pass only on exactly this many issues")
    args = ap.parse_args()
    issues = check(load())
    for where, item, rule, text in issues:
        print(f"[rule {rule}] {where} | {item} | {text}")
    print(f"\n{len(issues)} issue(s)")
    REPORTS.mkdir(exist_ok=True)
    out = REPORTS / f"link_check_{datetime.now():%Y%m%d_%H%M%S}.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["where", "item", "rule", "issue"])
        w.writerows(issues)
    print(f"Report: {out.relative_to(ROOT)}")
    if args.expect is not None:
        ok = len(issues) == args.expect
        print(f"Known-answer test: expected {args.expect}, got {len(issues)} - {'PASS' if ok else 'FAIL'}")
        return 0 if ok else 1
    return 0 if not issues else 1

if __name__ == "__main__":
    sys.exit(main())
