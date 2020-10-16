import json
import os
import requests

# Method that writes a list in a json file.
def write_in_json(outputFilePath: str, data: list) -> None:
    try:
        json_file = json.dumps(data, indent=4)
    except Exception as e:
        print(e)
        return

    if '.json' not in outputFilePath:
        outputFilePath += '.json'

    with open(outputFilePath, "w") as f:
        f.write(json_file)
    f.close()


def get_TOP_repo():
    # Start
    repos_list = []
    i = 1
    pages = 10

    # GitHub APIs has the limit of 100 repositories per page
    while (i <= pages):
        repo_stars_api = 'https://api.github.com/search/repositories?q=created:"2010-01-01..2010-12-31"language:python&sort=stars&order=desc&per_page=100&page=' + str(i)
        i += 1

        # get repos of api, return repos list
        r = requests.get(repo_stars_api)
        if r.status_code != 200:
            raise ValueError('Can not retrieve from {}'.format(repo_stars_api))
        repos_dict = json.loads(r.content)
        repos_list += repos_dict['items']

    # Repositories JSON with all information: stars, authors ...
    write_in_json(os.path.dirname(os.path.abspath(__file__)) + "/Top" + str(100*pages) + "_Python2010_Complete.json",
                  repos_list)

    # Repositories JSON with only the link ...
    with open(os.path.dirname(os.path.abspath(__file__)) + "/Top" + str(100*pages) + "_Python2019_Complete.json") as fh:
        articles = json.load(fh)

    article_urls = [article['html_url'] for article in articles]

    write_in_json(os.path.dirname(os.path.abspath(__file__)) + "/Top" + str(100*pages) + "_Python_UrlOnly.json",
                  article_urls)

    #End
    print("End")