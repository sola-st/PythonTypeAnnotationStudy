"""
Author: Luca Di Grazia
My personal library with useful Python methods.
Last update: June-2020
"""

import json

"""
Methods for multi-threading.
"""


# Chunkify list
def chunkify(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


"""
Methods for writing files.
"""


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