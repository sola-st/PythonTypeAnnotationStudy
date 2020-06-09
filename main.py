import os
import time
import multiprocessing
from Code import gitUtils
import logging
from Code.codeStatistics import CodeStatistics
from Code.projectUtils import *
from config import REPO_LIST

if __name__ == "__main__":
    logging.basicConfig(filename=config.ROOT_DIR + "/Resources/Output/app.log", filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s')

    if config.CLONING:
        gitUtils.repo_cloning(REPO_LIST, config.ROOT_DIR + "/GitHub")

    start = time.time()

    dirlist: list = [item for item in os.listdir(config.ROOT_DIR + "/GitHub") if
                     os.path.isdir(os.path.join(config.ROOT_DIR + "/GitHub", item))]

    code_changes: list = []

    statistics: CodeStatistics = CodeStatistics()

    lock = multiprocessing.Lock()

    if config.TEST:
        listOfStrings1 = [config.ROOT_DIR + "/GitHub/pythontest"] * 1

        for repo in listOfStrings1:
            print("\nWorking on pythontest")
            gitUtils.query_repo_get_changes("pythontest",
                                            '.py', statistics, code_changes, lock, logging)

    else:
        """
        threads: list = []
        for repository in dirlist:
            thread = threading.Thread(target=gitUtils.query_repo_get_changes,
                                      args=(repository, '.py', statistics,
                                            code_changes, lock, logging))
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
        """
        i = 1
        for repository in dirlist:
            print(i, '/', len(dirlist))
            i += 1
            gitUtils.query_repo_get_changes(repository,
                                            '.py', statistics, code_changes, lock, logging)

    if statistics.total_typeAnnotation_codeChanges > 0:
        # Statistics computation
        statistics.statistics_computation()
    else:
        print('No type annotation code changes found')
        exit()

    # Computational time
    end = time.time()
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)

    statistics.execution_time = "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)

    # Write results in files
    myplot(statistics)
    write_results(statistics, code_changes)

    print("\nProgram ends successfully in " + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))
