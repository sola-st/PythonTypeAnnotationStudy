import os
import pstats
from multiprocessing import Pool, cpu_count
import time
import multiprocessing
from Code import gitUtils
import logging
from Code.codeStatistics import CodeStatistics
from Code.projectUtils import *
from config import REPO_LIST
import cProfile
from tqdm import tqdm

if __name__ == "__main__":
   # logging.basicConfig(filename=config.ROOT_DIR + "/Resources/Output/app.log", filemode='w',
   #                     format='%(name)s - %(levelname)s - %(message)s')

    if config.CLONING:
        gitUtils.repo_cloning(REPO_LIST, config.ROOT_DIR + "/GitHub")

    start = time.time()

    dirlist: list = [item for item in os.listdir(config.ROOT_DIR + "/GitHub") if
                     os.path.isdir(os.path.join(config.ROOT_DIR + "/GitHub", item))]


    statistics_final: CodeStatistics = CodeStatistics()



    #lock = multiprocessing.Lock()

    process_statistics = []


    if config.TEST:
        profile = cProfile.Profile()
        profile.enable()

        print("\nWorking on TEST CONFIGURATION")
        gitUtils.query_repo_get_changes("mypy",
                                        '.py', statistics, code_changes, lock, logging, [1], 1)

        profile.disable()
        ps = pstats.Stats(profile).sort_stats('cumulative')
        ps.print_stats()
    else:
        #profile = cProfile.Profile()
        #profile.enable()

        process_list: list = []
        pointer = [1]
        dirlist_len = len(dirlist)

        """
        for repository in dirlist:
            #process_statistics.append(CodeStatistics())
            p = multiprocessing.Process(target=gitUtils.query_repo_get_changes,
                                      args=(repository, process_queue#, process_statistics[-1]
                                            #code_changes, # lock, logging,
                                            ))#pointer, dirlist_len))
            process_list.append(p)

        for p in process_list:
            p.start()

        for p in process_list:
            p.join()"""


        with Pool(multiprocessing.cpu_count()) as p:
            process_statistics += p.imap_unordered(gitUtils.query_repo_get_changes, dirlist)

        #profile.disable()
        #ps = pstats.Stats(profile).sort_stats('cumulative')
        #ps.print_stats()

        """
        i = 1
        for repository in dirlist:
            print(i, '/', len(dirlist))
            i += 1
            try:
                gitUtils.query_repo_get_changes(repository,
                                                '.py', statistics, code_changes, lock, logging, pointer, dirlist_len)
            except:
                print('Error in repository:', repository)
                continue
        """

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
        myplot(statistics_final)
        write_results(statistics_final, code_changes)
    except Exception as e:
        print('Error writing results in files: ' + str(e))

    print("\nProgram ends successfully in " + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))
