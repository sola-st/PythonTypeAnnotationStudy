import ast
import pathlib
import pstats
import subprocess
import time
import multiprocessing
from Code.TypeAnnotations import gitUtils, Utils
from Code.TypeAnnotations.get_TOP_repo import get_TOP_repo
from Code.TypeAnnotations.gitUtils import error_check
from Code.TypeAnnotations.projectUtils import *
import cProfile
from typed_ast import ast3

def typeAnnotation_analisis():


    if config.CLONING:
        i = 0
        j = [0]
        #while i < 10:
         #   gitUtils.repo_cloning_(config.ROOT_DIR + "/Resources/Input/Top1000_Python201"+str(i)+"_Complete.json", config.ROOT_DIR + "/GitHub", j)
          #  i += 1
        gitUtils.repo_cloning_oneplus(config.ROOT_DIR + "/Resources/Input/oneplus_list.json",
                              config.ROOT_DIR + "/GitHub", j)


    if config.STATISTICS_COMPUTATION:

        start = time.time()

        # List of repositories
        dirlist: list = [item for item in os.listdir(config.ROOT_DIR + "/GitHub") if
                         os.path.isdir(os.path.join(config.ROOT_DIR + "/GitHub", item))]

        # List of statistics from processes to be merged
        process_statistics = []

        if config.TEST:
            profile = cProfile.Profile()
            profile.enable()

            print("\nWorking on TEST CONFIGURATION")
            process_statistics += gitUtils.query_repo_get_changes("mypy")

            profile.disable()
            ps = pstats.Stats(profile).sort_stats('cumulative')
            ps.print_stats()
        else:

            with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
                process_statistics += p.imap_unordered(gitUtils.query_repo_get_changes, dirlist)

        code_changes: list = []
        commit_statistics: list = []

        # The statistics are merged from the processes
        statistics_final: CodeStatistics = CodeStatistics()

        statistics_final.merge_results(process_statistics, code_changes, commit_statistics)

        if statistics_final.total_typeAnnotation_codeChanges > 0:
            # Statistics computation
            try:
                statistics_final.statistics_computation()
            except Exception as e:
                print("Error during statistics computation",str(e))
        else:
            print('No type annotation code changes found')
            exit()

        # Computational time
        end = time.time()
        hours, rem = divmod(end - start, 3600)
        minutes, seconds = divmod(rem, 60)

        statistics_final.execution_time = "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)

        # Write results in files
        try:
            # Remove old files
            Utils.delete_all_files_in_folder(config.ROOT_DIR + '/Resources/Output/')

            # Compute new files
            write_results(statistics_final, code_changes, commit_statistics)
        except Exception as e:
            print('Error writing results in files:', str(e))

        print("\nStatistics computed in " + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))

    # Plots the results from the file Output/typeAnnotationAllStatisticsRAW.json
    if config.PLOT:
        statistics_final: CodeStatistics = load_final_statistics()
        myplot(statistics_final)



    print("\nProgram ends successfully")

if __name__ == "__main__":
    # Script configuration file in Code/TypeAnnotations/config.py

    typeAnnotation_analisis()
