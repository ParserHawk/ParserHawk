import subprocess
import time
import pandas as pd

Program_name = ["Large tran key", "ME1", "ME2 (16-bit key width)", "ME2 (8-bit key width)", "ME3"]
scripts = [
    "bin/make_tcam.py examples/Large_tran_key.txt --lookups 1 --lookup-width 4 --no-first-lookup-at-zero --save-tcam",
    "bin/make_tcam.py examples/ME1.txt --lookups 1 --lookup-width 1 --no-first-lookup-at-zero --save-tcam",
    "bin/make_tcam.py examples/ME2.txt --lookups 1 --lookup-width 2 --no-first-lookup-at-zero --save-tcam",
    "bin/make_tcam.py examples/ME2.txt --lookups 1 --lookup-width 1 --no-first-lookup-at-zero --save-tcam",
    "bin/make_tcam.py examples/ME3.txt --lookups 1 --lookup-width 2 --no-first-lookup-at-zero --save-tcam"
]
rows = []

for i in range(len(scripts)):
    row = [Program_name[i]]
    script = scripts[i]
    print(script.split())
    result = subprocess.run(
        ["python2"] + script.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    # print(result.stdout)
    match_count = result.stdout.count("# Match:")
    row.append(match_count)
    rows.append(row)

print(rows)
columns = [
    ("", "Program Name"),
    ("# TCAM", "DPParserGen"),
]

df = pd.DataFrame(rows, columns=pd.MultiIndex.from_tuples(columns))

col_widths = []
for col in df.columns:
    max_content_len = max(
        df[col].astype(str).map(len).max(),
        len(str(col))
    )
    col_widths.append(max_content_len)

df_centered = df.copy()
for i, col in enumerate(df.columns):
    df_centered[col] = df_centered[col].astype(str).map(lambda x: x.center(col_widths[i]))
    df_centered.rename(columns={col: str(col).center(col_widths[i])}, inplace=True)

print(df_centered.to_string(index=False))

df_centered.to_csv("table4.csv", index=False)