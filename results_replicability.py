from venv import create
from os.path import join, expanduser
from subprocess import run
from os.path import abspath
import script_typeAnnotation_analysis
import config
import sys

if 'fast' in sys.argv[1]:
	script_typeAnnotation_analysis.typeAnnotation_analisis()
	run(["python", abspath("PlotResultsAndComputeStats.py")], cwd=dir)
elif 'slow' in sys.argv[1]:
	config.CLONING = True
	config.EXTRACT = False
	config.STATISTICS_COMPUTATION = True
	script_typeAnnotation_analysis.typeAnnotation_analisis()
elif 'new' in sys.argv[1]:
	config.STATISTICS_COMPUTATION = True
	config.EXTRACT = False
	config.NORMAL_PRINT = True
	print('Extracting type annotations...')
	script_typeAnnotation_analysis.typeAnnotation_analisis()
else:
	print('Wrong argument: --slow or --fast or --new supported')
