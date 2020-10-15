import pstats
import time
import multiprocessing
from Code.TypeAnnotations import gitUtils, lucaUtils
from Code.TypeAnnotations.projectUtils import *
from config import REPO_LIST
import cProfile

def typeAnnotation_analisis():

    #repo_cloning_csv(config.ROOT_DIR + "/GitHub")

    if config.CLONING:
        gitUtils.repo_cloning(REPO_LIST, config.ROOT_DIR + "/GitHub")

    if config.STATISTICS_COMPUTATION:

        start = time.time()

        # List of repositories (already cloned)
        dirlist: list = [item for item in os.listdir(config.ROOT_DIR + "/GitHub") if
                         os.path.isdir(os.path.join(config.ROOT_DIR + "/GitHub", item))]

        # List of statistics from processes to be merged
        process_statistics = []

        if config.TEST:
            profile = cProfile.Profile()
            profile.enable()

            print("\nWorking on TEST CONFIGURATION")
            process_statistics += gitUtils.query_repo_get_changes("httpie-httpie")

            profile.disable()
            ps = pstats.Stats(profile).sort_stats('cumulative')
            ps.print_stats()
        else:

            with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
                process_statistics += p.imap_unordered(gitUtils.query_repo_get_changes, dirlist)

        code_changes: list = []
        commit_statistics: list = []

        # The statistics from processes are merged
        statistics_final: CodeStatistics = CodeStatistics()

        statistics_final.merge_results(process_statistics, code_changes, commit_statistics)

        if statistics_final.total_typeAnnotation_codeChanges > 0:
            # Statistics computation
            try:
                statistics_final.statistics_computation()
            except:
                print("Error during statistics computation")
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
            lucaUtils.delete_all_files_in_folder(config.ROOT_DIR + '/Resources/Output/')

            # Compute new files
            write_results(statistics_final, code_changes, commit_statistics)
        except Exception as e:
            print('Error writing results in files: ' + str(e))

        print("\nStatistics computed in " + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))

    # Plots the results from the file Output/typeAnnotationAllStatisticsRAW.json
    if config.PLOT:
        statistics_final: CodeStatistics = load_final_statistics()
        myplot(statistics_final)

    print("\nProgram ends successfully")

if __name__ == "__main__":
    # Script configuration file in Code/TypeAnnotations/config.py

    typeAnnotation_analisis()