import pstats
import time
import multiprocessing
from Code import gitUtils, lucaUtils
from Code.codeStatistics import CodeStatistics
from Code.projectUtils import *
from config import REPO_LIST
import cProfile

if __name__ == "__main__":

    if config.CLONING:
        gitUtils.repo_cloning(REPO_LIST, config.ROOT_DIR + "/GitHub")

    start = time.time()

    dirlist: list = [item for item in os.listdir(config.ROOT_DIR + "/GitHub") if
                     os.path.isdir(os.path.join(config.ROOT_DIR + "/GitHub", item))]

    statistics_final: CodeStatistics = CodeStatistics()

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

    statistics_final.merge_results(process_statistics, code_changes)

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
        myplot(statistics_final)
        write_results(statistics_final, code_changes)
    except Exception as e:
        print('Error writing results in files: ' + str(e))

    print("\nProgram ends successfully in " + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))
