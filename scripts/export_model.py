"""Export the cross table workbook to one CSV per sheet in model/.

The .ods is where people edit; the CSVs are what gets committed and what
agents and checks read. Run this after every edit, before committing.

Usage:  python scripts/export_model.py
"""
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "model" / "source" / "SafeStack_PLC-HMI_Cross_table.ods"
OUT = ROOT / "model"
HEADER_ROW = {"SafeStackPLCHMIInterfaceMap": 1}   # this sheet keeps a blank first row

def main() -> int:
    if not SOURCE.exists():
        print(f"Workbook not found: {SOURCE}")
        return 2
    for old in OUT.glob("crosstable_*.csv"):
        old.unlink()                               # a deleted sheet must not linger as a CSV
    for name in pd.ExcelFile(SOURCE, engine="odf").sheet_names:
        df = pd.read_excel(SOURCE, engine="odf", sheet_name=name, header=HEADER_ROW.get(name, 0))
        df = df.dropna(how="all")
        df = df[[c for c in df.columns if not (str(c).startswith("Unnamed") and df[c].isna().all())]]
        df.to_csv(OUT / f"crosstable_{name}.csv", index=False, encoding="utf-8")
        print(f"crosstable_{name}.csv  {len(df)} rows")
    return 0

if __name__ == "__main__":
    sys.exit(main())
