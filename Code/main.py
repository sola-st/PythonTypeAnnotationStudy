import os
import time

import config
from Code import gitUtils
from Code.codeChangeExtraction import writeJSON
from Code.codeStatistics import CodeStatistics

if __name__ == "__main__":
    if config.CLONING:
        gitUtils.repo_cloning(config.ROOT_DIR + '/Resources/Input/top30pythonRepo.json', config.ROOT_DIR + "/GitHub")

    start = time.time()

    dirlist = [item for item in os.listdir(config.ROOT_DIR + "/GitHub") if
               os.path.isdir(os.path.join(config.ROOT_DIR + "/GitHub", item))]

    code_changes = []

    statistics = CodeStatistics()

    if config.TEST:
        print("\nWorking on pythontest")
        code_changes += gitUtils.query_repo_get_commits(config.ROOT_DIR + "/GitHub/pythontest", '.py', statistics)
    else:
        for dir in dirlist:
            print("\nWorking on " + dir)
            code_changes += gitUtils.query_repo_get_commits(config.ROOT_DIR + "/GitHub/" + dir, '.py', statistics)

    statistics.percentageComputation()

    writeJSON("typeAnnotationChanges", code_changes)

    # Computational time
    end = time.time()
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)

    statistics.execution_time = "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)

    writeJSON("typeAnnotationStatistics", [statistics])



    print("\nProgram ends successfully in " + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))
