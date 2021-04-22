# Type Annotation Study

The study addresses questions regarding the prevalence, characteristics, and evolution of type annotations and type errors, grouped into four research questions:

* **RQ1**: How does the adoption of type annotations and the coverage evolution of type annotations evolve over time?
	We analyze this question at the ecosystem-level. We analyze the adoption trend of type annotations to understand the direction that developers are following when it comes to type annotations. The second part of this research question is an investigation about type annotation coverage considering all the program elements that could be annotated. This result can show the evolution and the actual state of type annotation adoption.
    
* **RQ2**: How does the usage of type annotations evolve over commits?
	This research question is useful to investigate the evolution of type annotations based on a commit-based timeline to have a more specific overview about development and trends of projects. In the first inspection, we study the type annotations trend based on commits. The results can be useful to search timeline patterns for type annotations. In the second inspection, we analyze all the commits of the developers that contribute to the projects with a specific focus on their contributions on type annotations. This analysis is useful to understand if there are developers more addicted to add type annotations, like "type annotation specialist" and how important is their contributions.
	
* **RQ3**: How does individual type annotations evolve over time?
	Answering this question is important because it helps us to understand if type annotations, once inserted, are maintained. Then, this question can be useful to understand if type annotations are added alongside other code changes or in specific commit with only type annotation code changes and which code locations are more annotated.
	
* **RQ4**: How much are type annotations and type error correlated?
	Answering this question can help us to study how the number and the nature of type errors evolve over time and whether the developers fix type errors. This question is important to find out if type annotations help to avoid type errors, so if they are helpful for building a more robust Python code.

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