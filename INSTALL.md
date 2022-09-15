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
