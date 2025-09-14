# ParserHawk

This repository contains the artifact for the ACM SIGCOMM '25 paper "[ParserHawk: Hardware-aware parser generator using program synthesis](https://github.com/ParserHawk/ParserHawk/blob/main/ParserHawk.pdf)".
The artifact consists of scripts to reproduce experiment results from the paper.

## Getting Started

### Setup

All experiments were run on CloudLab x86_64 c6620 nodes in the Utah cluster, using Ubuntu 22.04. Any similar Linux x86_64 machine would suffice (compilation time might be different). Clone this repository into your home directory. 

### Installing dependencies

* Install pip: ```sudo apt update```, ```sudo apt install python3-pip```
* Install necessary python packages: ```pip3 install -r requirements.txt```

### Executing program

* Table 3: 
Print results into table3.csv and table3orig.csv using the following command.
```
cd z3/cegis_loop/one_short_revision/P4_examples
python3 table3.py small # small is recommended (run for around 10 mins); medium takes 20 min or large takes 24h
python3 table3_nop.py small # small is recommended (run for around 15 mins)
```

* Table 4: 
Print results into table4.csv using the following command.
```
sudo apt install python2 
pip2 install pyparsing
cd DPParserGen/parser-gen/
source setup/env_setup.sh
``` 
```
python3 table4.py
```
Print results into table4_ParserHawk.csv using the following command.
```
cd z3/cegis_loop/one_short_revision/P4_examples
python3 table4_ParserHawk.py
```
* Table 5: 
Print results into table5.csv using the following command.
``` 
cd SIGCOMMAE/opt_effect
python3 table5.py
``` 