import pstats
import time
import multiprocessing
from Code.TypeAnnotations import gitUtils, Utils
from Code.TypeAnnotations.get_TOP_repo import get_TOP_repo
from Code.TypeAnnotations.gitUtils import error_check
from Code.TypeAnnotations.projectUtils import *
import cProfile

results_base_dir = config.ROOT_DIR + "/Resources/Output_typeErrors/"

def typeAnnotation_analisis():

    #error_check()

    #repo_cloning_csv(config.ROOT_DIR + "/GitHub")
    #get_TOP_repo() repositories_TOP100_2020

    if config.CLONING:
        i = 0
        j = [0]
        while i < 10:
            gitUtils.repo_cloning(config.ROOT_DIR + "/Resources/Input/Top1000_Python201"+str(i)+"_Complete.json", config.ROOT_DIR + "/GitHub", j)
            i += 1
        #gitUtils.repo_cloning(config.ROOT_DIR + "/Resources/Input/Top1000_Python2019_Complete.json",
         #                     config.ROOT_DIR + "/GitHub", j)


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
            repo_name = 'Python'
            with open(results_base_dir + "history_" + repo_name +".json") as fp:
                histories = json.load(fp)
            err_dict = dict()
            for h in histories:                
                err_dict[h['commit']] = dict()
                for w in h['all_warnings']: # TODO(wai): a lot of warnings in one commit, how to reduce?
                    f, l, c = w.split()[0].split(":")
                    if f not in err_dict[h['commit']]:
                        err_dict[h['commit']][f] = dict()
                    if l not in err_dict[h['commit']][f]:
                        err_dict[h['commit']][f][l] = dict()
                    err_dict[h['commit']][f][l][c] = w
            # TODO(wai): update insert/modify/remove logic
            # TODO(wai): some duplicate entries
            process_statistics += [gitUtils.query_repo_get_changes("Python", err_dict, ['cd987372e4c3a9f87d65b757ab46a48527fc9fa9', 'a5bcf0f6749a93a44f7a981edc9b0e35fbd066f2'])]            
            # Use a5bcf0f6749a93a44f7a981edc9b0e35fbd066f2 for checking function type extraction
            # process_statistics += [gitUtils.query_repo_get_changes("Python", err_dict, ['a5bcf0f6749a93a44f7a981edc9b0e35fbd066f2'])]            

            # Example (for checking a single commit and error):
            # https://github.com/TheAlgorithms/Python/commit/cd987372e4c3a9f87d65b757ab46a48527fc9fa9
            # parent = d668c172b07bf9f54d63dc295016a96ec782a541
            # process_statistics += [gitUtils.query_repo_get_changes("Python",  
            #     dict({    
            #         'd668c172b07bf9f54d63dc295016a96ec782a541': dict({
            #             'graphs/multi_heuristic_astar.py': dict({
            #                 '236': dict({
            #                     '30': "graphs/multi_heuristic_astar.py:236:30 Missing parameter annotation [2]: Parameter `n_heuristic` has no type specified."
            #                 })
            #             })
            #         })  
            #     }),
            #     ['cd987372e4c3a9f87d65b757ab46a48527fc9fa9']
            # )]

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