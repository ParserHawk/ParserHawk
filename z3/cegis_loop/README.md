# Polyglotter project (CEGIS loop part)

This folder shows how to run the CEGIS loop.

<!-- ## Description

An in-depth paragraph about your project and overview of use. -->

## Getting Started

<!-- ### Dependencies

* Install  -->

### Installing

* [p4c compiler](https://github.com/p4lang/p4c)
* z3: pip3 install z3-solver 

### Executing program
Using simple_p4_examples/simple_parser.p4 as an example

Step 1 (set environment variable): ```export P4C_HOME=<path_to_p4c>```

Step 2 (generate json file): ```$P4C_HOME/build/p4c --toJson /tmp/out.json simple_p4_examples/simple_parser.p4```

Step 3 (parse json file): ```python3 parse_p4.py```
