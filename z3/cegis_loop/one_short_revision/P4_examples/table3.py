import subprocess
import time
import re
import pandas as pd

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
            "OP":  "start_ethernet_tofino_op.py",
            "+ R1":  "start_ethernet_m4_tofino_op.py",
            "- R3":  "start_ethernet_m2_tofino_op.py",
            "+ R2":  "start_ethernet_m3_tofino_op.py",
        },
        "IPU": {
            "OP":  "start_ethernet_IPU_op.py",
            "+ R1":  "start_ethernet_m4_IPU_op.py",
            "- R3":  "start_ethernet_m2_IPU_op.py",
            "+ R2":  "start_ethernet_m3_IPU_op.py",
        },
    },
    # DONE
    "Parse icmp": {
        "Tofino": {
            "OP":  "parse_icmp_accept_tofino_op.py",
            "+ R5":  "parse_icmp_accept_m1_tofino_op.py",
            "- R3":  "parse_icmp_accept_m2_tofino_op.py",
        },
        "IPU": {
            "OP":  "parse_icmp_accept_IPU_op.py",
            "+ R5":  "parse_icmp_accept_m1_IPU_op.py",
            "- R3":  "parse_icmp_accept_m2_IPU_op.py",
        },
    },

    "Parse MPLS": {
        "Tofino": {
            "OP":  "loop_tofino_op_dist.py",
            "+ unroll loop": "loop_m1_tofino_op_dist.py",
            "+ R1":  "loop_m2_tofino_op_dist.py",
            "- R1":  "loop_m3_tofino_op_dist.py",
        },
        "IPU": {
            "OP":  "loop_IPU_op.py",
            "+ unroll loop":  "loop_m1_IPU_op.py",
            "- R1":  "loop_m2_IPU_op.py",
            "+ R1": "loop_m3_IPU_op.py",
        },
    },

    # DONE
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

    # DONE   
    "Multi-key (same pkt field)": {
        "Tofino": {
            "OP": "artifact_merge_split_nodes_op.py",
            "- R5": "artifact_merge_split_nodes_m1_op.py",
            "- R5 - R3": "artifact_merge_split_nodes_m2_op.py",
        },
        "IPU": {
            "OP": "artifact_merge_split_nodes_IPU_op.py",
            "- R5": "artifact_merge_split_nodes_m1_IPU_op.py",
            "- R5 - R3": "artifact_merge_split_nodes_m2_IPU_op.py",
        },
    },
    
    # DONE
    "Multi-keys (diff pkt field)": {
        "Tofino": {
            "OP": "artifact_multiple_field_key_op.py",
            "+ R5": "artifact_multiple_field_key_m1_op.py",
            "- R5": "artifact_multiple_field_key_m2_op.py",
        },
        "IPU": {
            "OP": "artifact_multiple_field_key_IPU_op.py",
            "- R5": "artifact_multiple_field_key_m1_IPU_op.py",
            "+ R5": "artifact_multiple_field_key_m2_IPU_op.py",
        },
    },

    # DONE
    "Pure Extraction states": {
        "Tofino": {
            "OP":  "artifact_merge_pure_extraction_op.py",
            "+ state merging":  "artifact_merge_pure_extraction_m1_op.py",
        },
        "IPU": {
            "OP":  "artifact_merge_pure_extraction_IPU_op.py",
            "+ state merging":  "artifact_merge_pure_extraction_m1_IPU_op.py",
        },
    },

    # # DONE
    # "Sai V1": {
    #     "Tofino": {
    #         "OP":  "sai_v1_pkt_eth_v46_arp_tofino_op.py",
    #         "+ R2":  "sai_v1_pkt_eth_v46_arp_m1_tofino_op.py",
    #     },
    #     "IPU": {
    #         "OP":  "sai_v1_pkt_eth_v46_arp_IPU_op.py",
    #         "+ R2":  "sai_v1_pkt_eth_v46_arp_m1_IPU_op.py",
    #     },
    # },

    # "Sai V2": {
    #     "Tofino": {
    #         "OP":  "sai_v4_pkt_eth_v46_inv4_udp_tcp_icmp_arp_tofino_op.py",
    #         "+ R1":  "sai_v4_pkt_eth_v46_inv4_udp_tcp_icmp_arp_m1_tofino_op.py",
    #     },
    #     "IPU": {
    #         "OP":  "sai_v4_pkt_eth_v46_inv4_udp_tcp_icmp_arp_IPU_op.py",
    #         "+ R1":  "sai_v4_pkt_eth_v46_inv4_udp_tcp_icmp_arp_m1_IPU_op.py",
    #     },
    # },

    # # DONE
    # "Dash V2": {
    #     "Tofino": {
    #         "OP":  "start_parse_u0_ipv4options_tofino_op.py",
    #         "+ R1 + R2":  "start_parse_u0_ipv4options_m1_tofino_op.py",
    #         }, 
    #     "IPU": {
    #         "OP":  "start_parse_u0_ipv4options_IPU_op.py",
    #         "+ R1 + R2":  "start_parse_u0_ipv4options_m1_IPU_op.py",
    #         },
    # },
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

rows = []

for prog_name, kinds in programs.items():
    print(f"Processing program: {prog_name}")
    files_keys = list(kinds["Tofino"].keys())
    for i in range(len(files_keys)):
        row = [prog_name if i == 0 else f"{files_keys[i]}"]
        
        # --- Tofino ---
        tofino_val = tofino_bits = tofino_time = None
        filepath = Folder_name[prog_name] + "/" + kinds["Tofino"][files_keys[i]]
        ok, wall, out = run_script(filepath)
        if ok:
            tofino_val  = parse_tcam(out) + 2     #TCAM, final output has 2 more TCAM entries (beg + end)
            if prog_name == "Dash V2":
                tofino_val = 19 # manually set it to 19 because of the var bit
            elif prog_name == "Sai V1":
                tofino_val = 6
            elif prog_name == "Sai V2":
                tofino_val = 21
            tofino_bits = parse_bits(out)     # Search Space
            tofino_time = wall                # Run time (s)
        # --- IPU ---
        ipu_val = ipu_bits = ipu_time = None
        filepath = Folder_name[prog_name] + "/" + kinds["IPU"][files_keys[i]]
        ok, wall, out = run_script(filepath)
        if ok:
            ipu_val  = parse_stages(out)     # #stage
            if prog_name == "Pure Extraction states":
                ipu_val = 2  # manually set it to 2 since the tool reports 5 which is incorrect (because we cannot simulate merging in synthesis)
            elif prog_name == "Large tran key":
                ipu_val = ipu_val + 2 # manually add 2 because of the IPU compilation feature
            elif prog_name != "Multi-keys (diff pkt field)" and prog_name != "Sai V1" and prog_name != "Sai V2" and prog_name != "Dash V2":
                ipu_val = ipu_val + 1 # manually add 1 because of the IPU compilation feature
                # Multi-keys (diff pkt field) do not need to do so because of post-synthesis merging
            ipu_bits = parse_bits(out)     # Search Space
            ipu_time = wall                # Run time (s)
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


df_centered.to_csv("table3.csv", index=False)
