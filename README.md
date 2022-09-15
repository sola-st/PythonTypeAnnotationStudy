# The Evolution of Type Annotations in Python: An Empirical Study

Type annotations and gradual type checkers attempt to reveal errors and facilitate maintenance  in dynamically typed programming languages. Despite the availability of these features and tools, it is currently unclear how quickly developers are adopting them, what strategies they follow when doing so, and whether adding type annotations reveals more type errors.

<p align="center">
<img src="Resources/img/fse0.png" alt="drawing" width="420"/>
</p>

This paper presents the first large-scale empirical study of the evolution of type annotations and type errors in Python. The study is based on an analysis of 1,414,936 type annotation changes, which we extract from 1,123,393 commits among 9,655 projects.
Our results show that (i) type annotations are getting more popular, and once added, often remain unchanged in the projects for a long time, (ii) projects follow three evolution patterns for type annotation usage -- regular annotation, type sprints, and occasional uses -- and that the used pattern correlates with the number of contributors, (iii) more type annotations help find more type errors (0.704 correlation), but nevertheless, many commits (78.3%) are committed despite having such errors. Our findings show that better developer training and automated techniques for adding type annotations are needed, as most code still remains unannotated, and they call for a better integration of gradual type checking into the development process.

<p float="left" align="center">
  <img src="Resources/img/fse1.png" width="370" />
  <img src="Resources/img/fse3.png" width="370" /> 
</p>


The paper has been accepted for the ESEC/FSE 2022 conference and it is avaible [online](https://www.software-lab.org/publications/FSE22TypeAnnotationsStudy.pdf).


**Reproduce the results**:
- Requirements:
```
Python 3.5+
```

- Run the following commands:

```
sudo apt install python3-pip
sudo apt install python3-virtualenv
virtualenv -p /usr/bin/python3 test-env
source test-env/bin/activate
pip3 install -r requirements.txt
python3 script_typeAnnotation_analysis.py
python3 ./PlotResultsAndComputeStats.py
```

- Wait around three minutes and the paper figures are in:
	- Figure  2: ./Resources/Output/annotationsPerYear2.pdf
	- Figure  3: ./Resources/Output/elements_annotated.pdf
	- Figure  4: ./Resources/Output_typeErrors/per_project/facebookresearch-pytext.pdf (and deepinsight-insightface.pdf and hhatto-autopep8.pdf)
	- Figure  5: ./Resources/Output/perc_annotations_lines_per_commit.pdf
	- Figure  7: ./Resources/Output/num_changes.pdf
	- Figure  9: ./Resources/Output/TopChanged_arg.pdf (and TopChanged_ret.pdf and TopChanged_var.pdf)
	- Figure 11: ./Resources/Output_typeErrors/errors_vs_annotations.pdf
	
- Algorithms:
 - Algorithm 1 -> File: ./Code/TypeAnnotations/codeChangeExtraction.py (from line 1367 to line 1664) 
 - Algorithm 2 -> File: ./Resources/Output_typeErrors/evolution_scirpt.py (full file)
	
- Research Questions:
 - RQ1.1: File: ./Code/TypeAnnotations/codeChangeExtraction.py (from line 1367 to line 1664)
 - RQ1.2: File ./Code/TypeAnnotations/gitUtils.py (from line 463 to line 468)
 - RQ2: File: ./Resources/Output_typeErrors/evolution_scirpt.py (full file)
 - RQ3.1: File ./Code/TypeAnnotations/gitUtils.py (from line 277 to line 343) 
 - RQ3.2: File ./Code/TypeAnnotations/codeChangeExtraction.py (line 1555)
 - RQ3.3: File ./Code/TypeAnnotations/codeChangeExtraction.py (from line 1461 to 1529)
 - RQ4.1: File ./script_AnalyzeRepo.py (from line 65 to line 123)
 - RQ4.2 and RQ4.3: File ./PlotResultsAndComputeStats.py (from line 70 to line 77), then line 340 and 342.
 
 The experiments are performed on a server with 48 Intel Xeon CPU cores clocked at 2.2GHz, 250GB of RAM, running Ubuntu 18.04.
	
- If you want to run all the experiments from scratch (~50 hours):

```
sudo apt install python3-pip
sudo apt install python3-virtualenv
virtualenv -p /usr/bin/python3 test-env
source test-env/bin/activate
pip3 install -r requirements.txt
python3 ./results_replicability.py --slow
```

**A usage example with a random repository**:
- Requirements:
```
Python 3.5+
```

- In ./GitHub run 'git clone https://github.com/httpie/httpie.git'
- Remove all the files from ./Resources/log
- Run the following command:

```
sudo apt install python3-pip
sudo apt install python3-virtualenv
virtualenv -p /usr/bin/python3 test-env
source test-env/bin/activate
pip3 install -r requirements.txt
python3 ./results_replicability.py --new
```
- Wait a few minutes and you can find the results in ./Resources/log/
