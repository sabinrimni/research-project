# ITU Research Project (Autumn 2019)

This repository contains the Research Project for the Autumn semester of 2019 by Rafał Markiewicz (rafm@itu.dk) and Sabin Rimniceanu (srim@itu.dk)

## Program Synthesis as Learning Rational Transductions

The subject area of this project focuses on applying Program Synthesis on string transduction tasks.  
String transduction is essentially a process of converting a string to another. It is widely used in Natural Language Processing to solve a range of tasks. This includes tasks such as spelling correction, grammatical error correction, grapheme to phoneme conversion, morphological inflection and even machine translation.

### Prerequisites

* The project has been built and tested using Python 3.6. Please download the latest version [here](https://www.python.org/downloads/).
* If running from the command line or Python Console, the following `pip` packages are required:
    * biopython
    * more-itertools
    * numpy
    * pandas
    * regex
    * subword-nmt

### Running the project

The simplest way to run the program is by navigating to the project root and typing `python runner.py`

### Data

The `data` folder in the project root contains the following structure:  
|-`data`  
|--`all` - contains all language files  
|--`latin_alphabet` - contains only languages using the latin alphabet  
|--`processed` - pre-generated intermediate files used for the various data processing steps  

**NOTE**: Any of the above step files can be regenerated using the method in the `runner.py` file called:  
`write_steps(generate_step_1=False, generate_step_2=False, generate_step_3=False, generate_step_4=False, generate_step_5=False)`  
By setting any of the steps to true will generate the appropriate files in the corresponding folder in the `./data/processed` folder.