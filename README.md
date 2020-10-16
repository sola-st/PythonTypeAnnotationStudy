# Type Annotation Study

The study addresses questions regarding the prevalence, characteristics, and evolution of type annotations and type errors, grouped into six research questions:

_Type Annotations_:
* **RQ1**: How prevalent are type annotations?
Answering this question helps understand whether type annotations play a significant role in Python at all, and what kinds of projects use them most.
* **RQ2**: What are the characteristics of type annotations, e.g., what code locations are annotated and with what types?
Answering this question could guide work on predicting type annotations automatically toward kinds of types that developers care about most.
* **RQ3**: How do type annotations evolve over time?
At the ecosystem-level, answering this question shows to what extent Python developers have been adopting type annotations since their introduction into the language.
At the level of individual annotations, understanding how developers add, remove, and updated type annotations could help in creating better tool support for this process.

_Type Errors_:
* **RQ4**: How prevalent are type errors?
Answering this question helps understand to what extent type annotations help in identifying programming errors.
It also reflects on whether type checking (and keeping code free of type errors) is already part of the typical development process.
* **RQ5**: What are the characteristic of type errors?
Answering this question can reveal common kinds of errors that developers should be aware of.
* **RQ6**: How do type errors evolve over time?

This question helps understand how type annotation-related code changes affect the type errors in a project.

**Repository Structure**

_Type Annotations_:

RQ1, RQ2 and RQ3 are computed simultaneously. 
The script to start the computation is ./script_typeAnnotation_analysis.py
Python files for this computation:
* Code/TypeAnnotations/codeChange.py -> code change class
* Code/TypeAnnotations/codeChangeExtraction.py -> Type Annotation analysis of a commit
* Code/TypeAnnotations/codeStatistics.py -> Statistics computation
* Code/TypeAnnotations/gitUtils.py -> repository analisis
* Code/TypeAnnotations/projectUtils.py -> plot methods
* Code/TypeAnnotations/lucaUtils.py -> utils
* Code/TypeAnnotations/get_TOP_repo.py -> extract top GitHub repositories

_Type Errors_: