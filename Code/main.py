import os
import time
import multiprocessing
import config
from Code import gitUtils, lucaUtils
from Code.codeStatistics import CodeStatistics
from Code.projectUtils import write_results

if __name__ == "__main__":
    if config.CLONING:
        gitUtils.repo_cloning(config.ROOT_DIR + '/Resources/Input/top30pythonRepo.json', config.ROOT_DIR + "/GitHub")

    start = time.time()

    dirlist = [item for item in os.listdir(config.ROOT_DIR + "/GitHub") if
               os.path.isdir(os.path.join(config.ROOT_DIR + "/GitHub", item))]

    code_changes = []

    statistics = CodeStatistics()  # type: CodeStatistics

    cpu_cores = multiprocessing.cpu_count()
    lock = multiprocessing.Lock()

    if config.TEST:
        listOfStrings1 = [config.ROOT_DIR + "/GitHub/pythontest"] * 1
        data_chunks = lucaUtils.chunkify(listOfStrings1, cpu_cores)

        #   for chunk in data_chunks:
        for repo in listOfStrings1:
            print("\nWorking on pythontest")
            code_changes += gitUtils.query_repo_get_changes(config.ROOT_DIR + "/GitHub/pythontest",
                                                            '.py', statistics, lock)
    else:
        for dir in dirlist:
            print("\nWorking on " + dir)
            code_changes += gitUtils.query_repo_get_changes(config.ROOT_DIR + "/GitHub/" + dir,
                                                            '.py', statistics, lock)

    # Statistics computation
    statistics.statistics_computation()

    # Computational time
    end = time.time()
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)

    statistics.execution_time = "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)

    # Write results in JSON files
    write_results(statistics, code_changes)

    print("\nProgram ends successfully in " + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))
