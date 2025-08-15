# ParserHawk

This repository contains the artifact for the ACM SIGCOMM '25 paper "ParserHawk: Hardware-aware parser generator using program synthesis".
The artifact consists of scripts to reproduce experiment results from the paper.

## Parser Synthesis using z3 solver

We leverage the z3 solver to output the target parser's behavior. 

<!-- ## Description

An in-depth paragraph about your project and overview of use. -->

## Getting Started

### Setup

All experiments were run on CloudLab x86_64 rs630 nodes in the Massachusetts cluster, using Ubuntu 22.04. Any similar Linux x86_64 machine would suffice. Clone this repository into your home directory. 

### Installing

* Install pip: ```sudo apt update```, ```sudo apt install python3-pip```
* Install necessary python packages: ```pip3 install -r requirements.txt```

### Executing program

* Table 3: 
* Table 4: 
```
sudo apt install python2 
pip2 install pyparsing
cd baseline/parser-gen/
source setup/env_setup.sh
``` 
```
python2 bin/make_tcam.py examples/Large_tran_key.txt --lookups 1 --lookup-width 4 --no-first-lookup-at-zero --save-tcam
python2 bin/make_tcam.py examples/ME1.txt --lookups 1 --lookup-width 1 --no-first-lookup-at-zero --save-tcam

python2 bin/make_tcam.py examples/ME3.txt --lookups 1 --lookup-width 2 --no-first-lookup-at-zero --save-tcam
```
* Table 5: 
Print results into table5.csv using the following command.
``` 
cd SIGCOMMAE/opt_effect
python3 table5.py
``` 