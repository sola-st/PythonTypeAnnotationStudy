from venv import create
from os.path import join, expanduser
from subprocess import run
from os.path import abspath
import script_typeAnnotation_analysis
import config
import sys

dir = join(expanduser("~"), "my-venv")
create(dir, with_pip=True)

# Install requirements
run(["bin/pip", "install", "-r", abspath("requirements.txt")], cwd=dir)

if 'fast' in sys.argv[1]:
	config.EXTRACT = True
	script_typeAnnotation_analysis.typeAnnotation_analisis()
	run(["python", abspath("PlotResultsAndComputeStats.py")], cwd=dir)
elif 'slow' in sys.argv[1]:
	config.CLONING = True
	config.STATISTICS_COMPUTATION = True
	script_typeAnnotation_analysis.typeAnnotation_analisis()
	run(["python", abspath("script_AnalyzeRepos.py")], cwd=dir)
	run(["python", abspath("PlotResultsAndComputeStats.py")], cwd=dir)
else:
	print('Wrong argument: --slow or --fast or --new supported')


