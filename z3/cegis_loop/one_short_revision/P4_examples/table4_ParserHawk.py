import subprocess
import time
import re
import pandas as pd
import argparse
import csv

# ===== map program name to folder name=====

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



columns = []
all_programs = ["LargeKey.py", "ME1.py", 'ME2_1.py','ME2_2.py','ME3.py']

for prog_name in all_programs:
    print(f"Processing program: {prog_name}")
    ok, wall, out = run_script("ME/"+prog_name)
    if ok:
        if "ME2_2.py" in prog_name:
            tofino_val  = parse_tcam(out) + 3     #TCAM, final output has 3 more TCAM entries 
        elif "ME3.py" in prog_name:
            tofino_val  = parse_tcam(out)
        else:
            tofino_val  = parse_tcam(out) + 2     #TCAM, final output has 2 more TCAM entries (beg + end)
        columns.append((prog_name[:-3], tofino_val))



with open("table4_ParserHawk.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Program", "# TCAM (ParserHawk)"])  # 表头
    writer.writerows(columns)