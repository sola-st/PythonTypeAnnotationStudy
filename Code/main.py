import config
from Code import gitUtils, parsers
from Code.codeChangeExtraction import extract_from_file

if __name__ == "__main__":

    gitUtils.query_repo_get_commits(config.ROOT_DIR + "/GitHub/pythontest", '.py')

    print("\nProgram ends successfully!")