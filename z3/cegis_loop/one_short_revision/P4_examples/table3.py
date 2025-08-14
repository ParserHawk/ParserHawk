import subprocess
import time
import re
import pandas as pd

# ===== map program name to folder name=====
Folder_name = {
    "Large tran key": "artifact_key_size",

}
programs = {
    "Large tran key": {
        "Tofino": {
            "OP":  "artifact_key_size_tofino_op.py",
            "+ R4":  "artifact_key_size_m1_tofino_op.py",
            "+ R1 + R4":  "artifact_key_size_m2_tofino_op.py",
            "+ R3 + R4":  "artifact_key_size_m4_tofino_op.py",
        },
        "IPU": {
            "OP":  "artifact_key_size_IPU_op.py",
            "+ R4":  "artifact_key_size_m1_IPU_op.py",
            "+ R1 + R4":  "artifact_key_size_m2_IPU_op.py",
            "+ R3 + R4":  "artifact_key_size_m4_IPU_op.py",
        },
    },
    # 继续加其它程序：
    # "Sai V1": {...}, "Dash V1": {...}
}

# 解析工具
def parse_bits(s):
    m = re.search(r"search_space_bit\s*=\s*(\d+)", s)
    return int(m.group(1)) if m else None

def parse_tcam(s):
    m = re.search(r"num of TCAM entry:\s*(\d+)", s, re.I)
    return int(m.group(1)) if m else None

def parse_stages(s):
    m = re.search(r"pipeline stages:\s*(\d+)", s, re.I)
    return int(m.group(1)) if m else None

def run_script(path):
    start = time.time()
    # print(f"Running {path}...")
    p = subprocess.run(
        ["python3", path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    wall = round(time.time() - start, 2)
    out = p.stdout or ""
    ok = ("Valid function found" in out)
    return ok, wall, out

rows = []
variant_order = ["OP", "+ R4", "+ R1 + R4", "+ R3 + R4"]

for prog_name, kinds in programs.items():
    for var in variant_order:
        row = [prog_name if var == "OP" else f"{var}"]
        # --- Tofino ---
        tofino_val = tofino_bits = tofino_time = None
        if "Tofino" in kinds and var in kinds["Tofino"]:
            filepath = Folder_name[prog_name] + "/" + kinds["Tofino"][var]
            ok, wall, out = run_script(filepath)
            if ok:
                tofino_val  = parse_tcam(out)     # #TCAM
                tofino_bits = parse_bits(out)     # Search Space
                tofino_time = wall                # Run time (s)

        # --- IPU ---
        ipu_val = ipu_bits = ipu_time = None
        if "IPU" in kinds and var in kinds["IPU"]:
            filepath = Folder_name[prog_name] + "/" + kinds["IPU"][var]
            ok, wall, out = run_script(filepath)
            if ok:
                ipu_val  = parse_stages(out)      # #Stages
                ipu_bits = parse_bits(out)        # Search Space
                ipu_time = wall                   # Run time (s)

        row.extend([
            tofino_val, tofino_bits, tofino_time,
            ipu_val,    ipu_bits,    ipu_time
        ])
        rows.append(row)

columns = [
    ("", "Program Name"),
    ("Tofino", "# TCAM"),
    ("Tofino", "Search Space (bits)"),
    ("Tofino", "OPT time (s)"),
    ("IPU", "# Stages"),
    ("IPU", "Search Space (bits)"),
    ("IPU", "OPT time (s)"),
]

df = pd.DataFrame(rows, columns=pd.MultiIndex.from_tuples(columns))

df = df.where(pd.notnull(df), None) 
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


df_centered.to_csv("run_ops_results_multiheader.csv", index=False)
