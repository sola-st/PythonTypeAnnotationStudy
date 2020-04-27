import json
import config
import difflib
import libcst as cst
from parsers import TypeCollector
from codeChange import CodeChange


def extract_from_file(file_path: str):
    with open(file_path, 'r') as file:
        src = file.read()

    # Parse file to AST
    ast = cst.parse_module(src)

    # Collect types
    type_collector = TypeCollector()
    ast.visit(type_collector)

    param_types = type_collector.param_annotations
    return_types = type_collector.return_types

    #print(f"params: {param_types}, returns: {return_types}")
    #return f"params: {param_types}, returns: {return_types}"
    return param_types,return_types

def writeJSON(filename, change_list):
    """
    try:
        with open(config.ROOT_DIR + "/Resources/Output/" + filename + ".json") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    if not data:
        data = {}
    """
    # data = [object]

    s = json.dumps([change.__dict__ for change in change_list])

    with open(config.ROOT_DIR + "/Resources/Output/" + filename + ".json", "w") as f:
        json.dump(s, f, indent=4)


def search_multiple_strings_in_file(file_name, list_of_strings):
    """Get line from the file along with line numbers, which contains any string from the list"""
    line_number = 0
    list_of_results = []
    # Open the file in read only mode
    with open(file_name, 'r') as read_obj:
        # Read all lines in the file one by one
        for line in read_obj:
            line_number += 1
            # For each line, check if line contains any string from the list of strings
            for string_to_search in list_of_strings:
                if string_to_search in line:
                    # If any string is found in line, then append that line along with line number in list
                    list_of_results.append((string_to_search, line_number, line.rstrip()))

    # Return list of tuples containing matched string, line numbers and lines where string is found
    return list_of_results

if __name__ == "__main__":
    old_param_types, old_return_types  = extract_from_file('/home/luca/PycharmProjects/TypeAnnotation_Study/Resources/Input/old.py')

    new_param_types, new_return_types = extract_from_file('/home/luca/PycharmProjects/TypeAnnotation_Study/Resources/Input/new.py')

    print(old_param_types)
    print(new_param_types)

    print("\n")

    print(old_return_types)
    print(new_return_types)

    for key in old_return_types:
        pass

   # diff=difflib.unified_diff(old, new)

   # print("".join(diff))


    change_list = []
    change_list.append(CodeChange("3jdi32d3", "234", "if(x>)", "while(x<0)"))
    change_list.append(CodeChange("3jdi32d3", "234", "if(x>)", "while(x<0)"))
 #   writeJSON("typeAnnotationChanges", change_list)

