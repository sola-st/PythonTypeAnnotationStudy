import json
import os
import subprocess

import config
from Code.codeChange import CodeChange
from Code.parsers import TypeCollector
import libcst as cst


def extract_from_snippet(string):
    if len(string) == 0:
        return {}, {}

    # Parse file to AST
    ast = cst.parse_module(string[2:-1].replace("\\n", os.linesep))

    # Collect types
    type_collector = TypeCollector()
    ast.visit(type_collector)

    param_types = type_collector.param_annotations
    return_types = type_collector.return_types

    # print(f"params: {param_types}, returns: {return_types}")
    # return f"params: {param_types}, returns: {return_types}"
    return param_types, return_types


def extract_from_file(file_path: str):
    with open(file_path, 'r') as file:
        src = file.read()

    print(src)
    # Parse file to AST
    ast = cst.parse_module(src)

    # Collect types
    type_collector = TypeCollector()
    ast.visit(type_collector)

    param_types = type_collector.param_annotations
    return_types = type_collector.return_types

    # print(f"params: {param_types}, returns: {return_types}")
    # return f"params: {param_types}, returns: {return_types}"
    return param_types, return_types


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
                if ''.join(string_to_search) in line:
                    # If any string is found in line, then append that line along with line number in list
                    list_of_results.append((string_to_search, line_number, line.rstrip()))

    # Return list of tuples containing matched string, line numbers and lines where string is found
    return list_of_results


def search_key_value_in_file(file_name, list_of_strings):
    """Get line from the file along with line numbers, which contains any string from the list"""
    line_number = 0
    # Open the file in read only mode
    with open(file_name, 'r') as read_obj:
        # Read all lines in the file one by one
        for line in read_obj:
            line_number += 1
            # TODO: Add regex for edge cases
            str = "(".join(list_of_strings[0])
            str2 = "".join(list_of_strings[1])
            l = line
            if "(".join(list_of_strings[0]) in line and "".join(list_of_strings[1]) in line.replace(" ", ""):
                # If any string is found in line, then append that line along with line number in list
                return line_number, l.rstrip()

    # Return list of tuples containing matched string, line numbers and lines where string is found
    return False


def TypeAnnotationExtraction(repo_path, commit, patch, url):
    # command = "git --git-dir " + str(repo_path) + '/.git show ' + str(commit.hex) + ":" + str(patch.delta.old_file.path)
    # os.system(command)
    code_changes = []

    old_out = subprocess.Popen(
        ["git", "--git-dir", str(repo_path) + '/.git', 'show', str(commit.hex) + ":" + str(patch.delta.old_file.path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    old_stdout, old_stderr = old_out.communicate()

    old_param_types, old_return_types = extract_from_snippet(str(old_stdout))

    new_out = subprocess.Popen(["git", "--git-dir", str(repo_path) + '/.git', 'show',
                                str('^' + commit.hex) + ":" + str(patch.delta.new_file.path)],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    new_stdout, new_stderr = new_out.communicate()

    new_param_types, new_return_types = extract_from_snippet(str(new_stdout))

    for key in old_return_types:
        if old_return_types[key] != new_return_types[key]:
            old_line, old_code = search_key_value_in_file(config.ROOT_DIR + '/Resources/Input/old.py',
                                                          [key, old_return_types[key]])
            new_line, new_code = search_key_value_in_file(config.ROOT_DIR + '/Resources/Input/new.py',
                                                          [key, new_return_types[key]])

            code_changes.append(
                CodeChange(url, str(patch.delta.old_file.path), old_line, old_code, str(patch.delta.new_file.path),
                           new_line, new_code))

    for key in old_param_types:
        s = old_param_types[key]
        ss = new_param_types[key]
        if old_param_types[key] != new_param_types[key]:
            old_line, old_code = search_key_value_in_file(config.ROOT_DIR + '/Resources/Input/old.py',
                                                          [key, old_param_types[key]])
            new_line, new_code = search_key_value_in_file(config.ROOT_DIR + '/Resources/Input/new.py',
                                                          [key, new_param_types[key]])

            code_changes.append(
                CodeChange(url, str(patch.delta.old_file.path), old_line, old_code, str(patch.delta.new_file.path),
                           new_line, new_code))

        return code_changes


def writeJSON(filename, change_list):
    json_file = json.dumps([change.__dict__ for change in change_list], indent=4)

    print(json_file)

    with open(config.ROOT_DIR + "/Resources/Output/" + filename + ".json", "w") as f:
        f.write(json_file)
    f.close()
