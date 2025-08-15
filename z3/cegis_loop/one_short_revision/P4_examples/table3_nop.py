import subprocess
import time
import re
import pandas as pd
import argparse


# ===== map program name to folder name=====
Folder_name = {
    "Large tran key": "artifact_key_size",
    "Parse icmp": "parse_icmp_accept",
    "Pure Extraction states": "artifact_merge_pure_extraction",
    "Multi-key (same pkt field)": "artifact_merge_split_nodes",
    "Multi-keys (diff pkt field)": "artifact_multiple_field_key",
    "Parse Ethernet": "start_ethernet",
    "Sai V1": "sai_v1_pkt_eth_v46_arp",
    "Sai V2": "sai_v4_pkt_eth_v46_inv4_udp_tcp_icmp_arp",
    "Dash V2": "dash_start_parse_u0_ipv4options",
    "Parse MPLS": "loop",
}
programs = {
    "Parse Ethernet": { 
        "Tofino": {
            "OP":  "start_ethernet_tofino.py",
            "+ R1":  "start_ethernet_m4_tofino.py",
            "- R3":  "start_ethernet_m2_tofino.py",
            "+ R2":  "start_ethernet_m3_tofino.py",
        },
        "IPU": {
            "OP":  "start_ethernet_IPU.py",
            "+ R1":  "start_ethernet_m4_IPU.py",
            "- R3":  "start_ethernet_m2_IPU.py",
            "+ R2":  "start_ethernet_m3_IPU.py",
        },
    },

    # DONE   
    "Multi-key (same pkt field)": {
        "Tofino": {
            "OP": "artifact_merge_split_nodes.py",
            "- R5": "artifact_merge_split_nodes_m1.py",
            "- R5 - R3": "artifact_merge_split_nodes_m2.py",
        },
        "IPU": {
            "OP": "artifact_merge_split_nodes_IPU.py",
            "- R5": "artifact_merge_split_nodes_m1_IPU.py",
            "- R5 - R3": "artifact_merge_split_nodes_m2_IPU.py",
        },
    },
    
}

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

parser = argparse.ArgumentParser()
parser.add_argument("size", choices=["small", "medium", "large"], help="Run scale: small / medium / large")
args = parser.parse_args()

if args.size == "small":
    programs = programs
elif args.size == "medium":
    programs = programs
else:
    programs = programs
rows = []

for prog_name, kinds in programs.items():
    print(f"Processing program: {prog_name}")
    files_keys = list(kinds["Tofino"].keys())
    for i in range(len(files_keys)):
        row = [prog_name if i == 0 else f"{files_keys[i]}"]
        
        # --- Tofino ---
        tofino_time = None
        filepath = Folder_name[prog_name] + "/" + kinds["Tofino"][files_keys[i]]
        ok, wall, out = run_script(filepath)
        if ok:
            tofino_time = wall                # Run time (s)
        # --- IPU ---
        ipu_val = ipu_bits = ipu_time = None
        filepath = Folder_name[prog_name] + "/" + kinds["IPU"][files_keys[i]]
        ok, wall, out = run_script(filepath)
        if ok:
            ipu_time = wall                # Run time (s)
        row.extend([
            tofino_time,
            ipu_time
        ])
        rows.append(row)

columns = [
    ("", "Program Name"),
    ("Tofino", "Orig time (s)"),
    ("IPU", "Orig time (s)"),
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


df_centered.to_csv("table3orig.csv", index=False)
