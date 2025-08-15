import subprocess
import time
import pandas as pd

programs = {
    "Sai V1": [
        "sai/others.py",
        "sai/opt5.py",
        "sai/opt45.py",
        "sai/sai_IPU_others.py",
        "sai/sai_IPU_opt5.py",
        "sai/sai_IPU_opt45.py",
    ],
    "Dash V1": [
        "dash/others.py",
        "dash/opt5.py",
        "dash/opt45.py",
        "dash/dash_IPU_others.py",
        "dash/dash_IPU_opt5.py",
        "dash/dash_IPU_opt45.py",
    ],
    "Large tran key": [
        "artifact_key_size/others.py",
        "artifact_key_size/opt5.py",
        "artifact_key_size/opt45.py",
        "artifact_key_size/artifact_key_size_IPU_others.py",
        "artifact_key_size/artifact_key_size_IPU_opt5.py",
        "artifact_key_size/artifact_key_size_IPU_opt45.py",
    ],
}

rows = []
for prog_name, scripts in programs.items():
    row = [prog_name]
    for script in scripts:
        start = time.time()
        result = subprocess.run(
            ["python3", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        end = time.time()
        output = result.stdout
        if "Valid function found" in output:
            row.append(round(end - start, 2))
        else:
            row.append(None)
    rows.append(row)

columns = [
    ("", "Program Name"),
    ("Tofino", "Other OPT (s)"),
    ("Tofino", "+OPT5 (s)"),
    ("Tofino", "+OPT4, 5 (s)"),
    ("IPU", "Other OPT (s)"),
    ("IPU", "+OPT5 (s)"),
    ("IPU", "+OPT4, 5 (s)")
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

df_centered.to_csv("table5.csv", index=False)