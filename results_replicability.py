from venv import create
from os.path import join, expanduser
from subprocess import run
from os.path import abspath
import script_typeAnnotation_analysis

dir = join(expanduser("~"), "my-venv")
create(dir, with_pip=True)

# where requirements.txt is in same dir as this script
run(["bin/pip", "install", "-r", abspath("requirements.txt")], cwd=dir)

# Type Annotations results
script_typeAnnotation_analysis.typeAnnotation_analisis()
run(["python", abspath("PlotResultsAndComputeStats.py")], cwd=dir)
