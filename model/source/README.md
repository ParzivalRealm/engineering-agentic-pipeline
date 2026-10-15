# model/source/ - where people edit

`SafeStack_PLC-HMI_Cross_table.ods` lives here, under that name, forever.
No v2, v3 or "final" in the filename: Git keeps the versions.

After every edit: save, run `py scripts\export_model.py`, run the link check,
then commit the .ods and the regenerated CSVs together.
