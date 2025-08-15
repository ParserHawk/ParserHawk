import subprocess, re

cmd = ["python2", "bin/make_tcam.py", "examples/headers-simple.txt"]
out = subprocess.check_output(cmd).decode("utf-8", "ignore")

count = len(re.findall(r"# Match:", out))
print("TCAM entries:", count)
