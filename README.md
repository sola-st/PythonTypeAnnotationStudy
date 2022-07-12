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

- Run the following command:

```
python3 ./results_replicability.py --fast
```

- Wait around three minutes and the paper figures are in:
	- Figure  2: ./Resources/Output/annotationsPerYear2.pdf
	- Figure  3: ./Resources/Output/elements_annotated.pdf
	- Figure  4: ./Resources/Output/Output_typeErrors/per_project/facebookresearch-pytext.pdf (and deepinsight-insightface.pdf and hhatto-autopep8.pdf)
	- Figure  5: ./Resources/Output/perc_annotations_lines_per_commit.pdf
	- Figure  7: ./Resources/Output/num_changes.pdf
	- Figure  9: ./Resources/Output/TopChanged_arg.pdf (and TopChanged_ret.pdf and TopChanged_var.pdf)
	- Figure 10: ./Resources/Output/Output_typeErrors/errors_vs_annotations.pdf
	
- If you want to run all the experiments from scratch (~50 hours):

```
python3 ./results_replicability.py --slow
```

**Run tool on a different dataset**:
- Requirements:
```
Python 3.5+
```

- Clone all your repositories in ./GitHub
- Remove all the files from ./Resources/Output/ and ./Resources/Output/Output_typeErrors/ and ./Resources/log
- Run the following command:

```
python3 ./results_replicability.py --new
