import os
import time

import config
from Code import gitUtils
from Code.codeChangeExtraction import writeJSON

if __name__ == "__main__":
    start = time.time()

    dirlist = [item for item in os.listdir(config.ROOT_DIR + "/GitHub") if
               os.path.isdir(os.path.join(config.ROOT_DIR + "/GitHub", item))]

    code_changes = []

    for dir in dirlist:
        print("\nWorking on " + dir)
        code_changes += gitUtils.query_repo_get_commits(config.ROOT_DIR + "/GitHub/" + dir, '.py')


    # add statistics

    writeJSON("typeAnnotationChanges", code_changes)

    # Computational time
    end = time.time()
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)

    print("\nProgram ends successfully in " + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))
