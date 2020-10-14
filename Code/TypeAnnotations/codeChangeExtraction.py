import re
import pathlib
import subprocess
import config
from Code.TypeAnnotations.codeChange import CodeChange, SingleDiffChange
from Code.parsers import TypeCollector
import libcst as cst
import copy
from libcst.metadata import PositionProvider


def extract_from_snippet(string):
    if len(string) == 0:
        return {}, {}, {}

    # Parse file to AST
    # try:
    # str_file = string[2:-1].replace("\\n", os.linesep).replace("\\t", "    ").replace("= \\'", "= '").replace("\\\\", "\\")
    # ast = cst.parse_module(string[2:-1].replace("\\n", os.linesep).replace("\\t", "    "))

    string = "from typing import Any\n" + "def process_something(arguments: Any, fooo: complex) -> None:\n   pass\nx:List[int] = []"

    ast = cst.parse_module(string)

    # except Exception as e:
    # print('Failed to upload to ftp: ' + str(e))
    # return {}, {}, {}

    # Pre-compute scopes
    wrapper = cst.metadata.MetadataWrapper(ast)
    scopes = set(wrapper.resolve(cst.metadata.ScopeProvider).values())

    # Collect types
    type_collector = TypeCollector()
    type_collector.wrapper = wrapper
    wrapper.visit(type_collector)

    param_types = type_collector.param_annotations
    return_types = type_collector.return_types
    variable_types = type_collector.variable_annotations

    # print(f"params: {param_types}, returns: {return_types}")
    # return f"params: {param_types}, returns: {return_types}"
    return param_types, return_types, variable_types


def extract_from_snippet_new(string_old, string_new):
    if len(string_old) == 0:
        return {}, {}, {}

    # string_old = "from typing import Any\n" + "def process_something(arguments: Any, func:int, f2:str, fooo)-> int:\n " \
    #  "  pass\nx:List[int] = []\ny:List[int] = []\nx = 0 "

    # string_new = "from typing import Any\n" + "def process_something(arguments: Any, func, f2:float, fooo: " \
    # "complex):\n   pass\nx = []\ny:Tuple[int] = []\nx:float = 0 "

    ast_old = cst.parse_module(string_old)
    wrapper_old = cst.metadata.MetadataWrapper(ast_old)
    positions_old = wrapper_old.resolve(PositionProvider)
    node_list_old = []

    ast_new = cst.parse_module(string_new)
    wrapper_new = cst.metadata.MetadataWrapper(ast_new)
    positions_new = wrapper_new.resolve(PositionProvider)
    node_list_new = []

    node_var_list_old = []
    node_var_list_new = []

    # For the old file
    for node, pos in positions_old.items():
        if 'FunctionDef' in type(node).__name__:
            if hasattr(node, 'params') or hasattr(node, 'returns'):
                if hasattr(node.params, 'params'):
                    node_list_old.append(node)
                #     for parameter in node.params.params:
                #         if hasattr(parameter, 'annotation'):
                #             if hasattr(parameter.annotation, 'annotation'):
                #                 if hasattr(parameter.annotation.annotation, 'value'):
                #                     if hasattr(parameter.annotation.annotation.value, 'value'):
                #                         print('[ARG] ', parameter.annotation.annotation.value.value, '->', pos)
                #                     else:
                #                         print('[ARG] ', parameter.annotation.annotation.value, '->', pos)
                # if hasattr(node, 'returns'):
                #     if hasattr(node.returns, 'annotation'):
                #         if hasattr(node.returns.annotation, 'value'):
                #             print('[RETURN] ', node.returns.annotation.value, '->', pos)
        else:
            if 'SimpleStatementLine' in type(node).__name__:
                if hasattr(node, 'body'):
                    for variable in node.body:
                        if hasattr(variable, 'annotation'):
                            node_var_list_old.append(node)
                            # pass
                            # node_list_old.append(node)
                            # if hasattr(variable.annotation, 'annotation'):
                            #     if hasattr(variable.annotation.annotation, 'value'):
                            #         if hasattr(variable.annotation.annotation.value, 'value'):
                            #             print('[VAR] ', variable.annotation.annotation.value.value, '->', pos)
                            #         else:
                            #             print('[VAR] ', variable.annotation.annotation.value, '->', pos)

    print(' ')
    # For the new file
    for node, pos in positions_new.items():
        if 'FunctionDef' in type(node).__name__:
            if hasattr(node, 'params') or hasattr(node, 'returns'):
                if hasattr(node.params, 'params'):
                    node_list_new.append(node)
                #     for parameter in node.params.params:
                #         if hasattr(parameter, 'annotation'):
                #             if hasattr(parameter.annotation, 'annotation'):
                #                 if hasattr(parameter.annotation.annotation, 'value'):
                #                     if hasattr(parameter.annotation.annotation.value, 'value'):
                #                         print('[ARG] ', parameter.annotation.annotation.value.value, '->', pos)
                #                     else:
                #                         print('[ARG] ', parameter.annotation.annotation.value, '->', pos)
                # if hasattr(node, 'returns'):
                #     if hasattr(node.returns, 'annotation'):
                #         if hasattr(node.returns.annotation, 'value'):
                #             print('[RETURN] ', node.returns.annotation.value, '->', pos)
        else:
            if 'SimpleStatementLine' in type(node).__name__:
                if hasattr(node, 'body'):
                    for variable in node.body:
                        if hasattr(variable, 'annotation'):
                            node_var_list_new.append(node)
                            # pass
                            # node_list_new.append(node)
                            # if hasattr(variable.annotation, 'annotation'):
                            #     if hasattr(variable.annotation.annotation, 'value'):
                            #         if hasattr(variable.annotation.annotation.value, 'value'):
                            #             print('[VAR] ', variable.annotation.annotation.value.value, '->', pos)
                            #         else:
                            #             print('[VAR] ', variable.annotation.annotation.value, '->', pos)

    return node_list_old, node_list_new, node_var_list_old, node_var_list_new


def extract_from_snippet_new_new(string_old, string_new):
    # if len(string_old) == 0:
    #   return {}, {}, {}

    # string_old = "from typing import Any\n" + "def process_something(arguments: Any, func:int, f2:str, fooo)-> int:\n " \
    #                                          "  pass\nx:List[int] = []\ny:List[int] = []\nx = 0 "

    # string_new = "from typing import Any\n" + "def process_something(arguments: Any, func, f2:float, fooo: " \
    #                                         "complex):\n   pass\nx = []\ny:Tuple[int] = []\nx:float = 0 "

    node_list_new = []
    node_list_old = []

    if not ("fatal: Path" in str(string_old) and "does not exist in" in str(string_old)):
        ast_old = cst.parse_module(string_old)
        wrapper_old = cst.metadata.MetadataWrapper(ast_old)
        positions_old = wrapper_old.resolve(PositionProvider)

        # For the old file
        for node, pos in positions_old.items():
            if 'FunctionDef' in type(node).__name__:
                if hasattr(node, 'params') or hasattr(node, 'returns'):
                    if hasattr(node.params, 'params'):
                        # node_list_old.append(node)
                        for parameter in node.params.params:
                            if hasattr(parameter, 'annotation'):
                                if hasattr(parameter.annotation, 'annotation'):
                                    if hasattr(parameter.annotation.annotation, 'value'):
                                        if hasattr(parameter.annotation.annotation.value, 'value'):
                                            # print('[ARG] ', parameter.annotation.annotation.value.value, '->', pos)
                                            annotation_node = SingleDiffChange('argument', 'old', parameter.name.value,
                                                                               parameter.annotation.annotation.value.value,
                                                                               pos.start.line)
                                            node_list_old.append(annotation_node)
                                        else:
                                            # print('[ARG2] ', parameter.annotation.annotation.value, '->', pos)
                                            annotation_node = SingleDiffChange('argument', 'old', parameter.name.value,
                                                                               parameter.annotation.annotation.value,
                                                                               pos.start.line)
                                            node_list_old.append(annotation_node)

                    if hasattr(node, 'returns'):
                        if hasattr(node.returns, 'annotation'):
                            if hasattr(node.returns.annotation, 'value'):
                                # print('[RETURN] ', node.returns.annotation.value, '->', pos)
                                annotation_node = SingleDiffChange('return', 'old', node.name.value,
                                                                   node.returns.annotation.value, pos.start.line)
                                node_list_old.append(annotation_node)
            else:
                if 'SimpleStatementLine' in type(node).__name__:
                    if hasattr(node, 'body'):
                        for variable in node.body:
                            if hasattr(variable, 'annotation'):
                                if hasattr(variable.annotation, 'annotation'):
                                    if hasattr(variable.annotation.annotation, 'value'):
                                        if hasattr(variable.annotation.annotation.value, 'value'):
                                            # print('[VAR] ', variable.annotation.annotation.value.value, '->', pos)
                                            annotation_node = SingleDiffChange('variable', 'old', variable.target.value,
                                                                               variable.annotation.annotation.value.value,
                                                                               pos.start.line)
                                            node_list_old.append(annotation_node)
                                        else:
                                            # print('[VAR2] ', variable.annotation.annotation.value, '->', pos)
                                            annotation_node = SingleDiffChange('variable', 'old', variable.target.value,
                                                                               variable.annotation.annotation.value,
                                                                               pos.start.line)
                                            node_list_old.append(annotation_node)

    if not ("fatal: Path" in str(string_new) and "does not exist in" in str(string_new)):
        ast_new = cst.parse_module(string_new)
        wrapper_new = cst.metadata.MetadataWrapper(ast_new)
        positions_new = wrapper_new.resolve(PositionProvider)

        # For the new file
        for node, pos in positions_new.items():
            if 'FunctionDef' in type(node).__name__:
                if hasattr(node, 'params') or hasattr(node, 'returns'):
                    if hasattr(node.params, 'params'):
                        for parameter in node.params.params:
                            if hasattr(parameter, 'annotation'):
                                if hasattr(parameter.annotation, 'annotation'):
                                    if hasattr(parameter.annotation.annotation, 'value'):
                                        if hasattr(parameter.annotation.annotation.value, 'value'):
                                            # print('[ARG] ', parameter.annotation.annotation.value.value, '->', pos)
                                            annotation_node = SingleDiffChange('argument', 'new', parameter.name.value,
                                                                               parameter.annotation.annotation.value.value,
                                                                               pos.start.line)
                                            node_list_new.append(annotation_node)
                                        else:
                                            # print('[ARG2] ', parameter.annotation.annotation.value, '->', pos)
                                            annotation_node = SingleDiffChange('argument', 'new', parameter.name.value,
                                                                               parameter.annotation.annotation.value,
                                                                               pos.start.line)
                                            node_list_new.append(annotation_node)
                    if hasattr(node, 'returns'):
                        if hasattr(node.returns, 'annotation'):
                            if hasattr(node.returns.annotation, 'value'):
                                # print('[RETURN] ', node.returns.annotation.value, '->', pos)
                                annotation_node = SingleDiffChange('return', 'new', node.name.value,
                                                                   node.returns.annotation.value, pos.start.line)
                                node_list_new.append(annotation_node)
            else:
                if 'SimpleStatementLine' in type(node).__name__:
                    if hasattr(node, 'body'):
                        for variable in node.body:
                            if hasattr(variable, 'annotation'):
                                if hasattr(variable.annotation, 'annotation'):
                                    if hasattr(variable.annotation.annotation, 'value'):
                                        if hasattr(variable.annotation.annotation.value, 'value'):
                                            # print('[VAR] ', variable.annotation.annotation.value.value, '->', pos)
                                            annotation_node = SingleDiffChange('variable', 'new', variable.target.value,
                                                                               variable.annotation.annotation.value.value,
                                                                               pos.start.line)
                                            node_list_new.append(annotation_node)
                                        else:
                                            # print('[VAR2] ', variable.annotation.annotation.value, '->', pos)
                                            annotation_node = SingleDiffChange('variable', 'new', variable.target.value,
                                                                               variable.annotation.annotation.value,
                                                                               pos.start.line)
                                            node_list_new.append(annotation_node)

    return node_list_old, node_list_new


def extract_from_file(file_path: str):
    with open(file_path, 'r') as file:
        src = file.read()

    # Parse file to AST
    try:
        ast = cst.parse_module(src)
    except:
        return {}, {}, {}

    # Pre-compute scopes
    wrapper = cst.metadata.MetadataWrapper(ast)
    scopes = set(wrapper.resolve(cst.metadata.ScopeProvider).values())

    # Collect types
    type_collector = TypeCollector()
    wrapper.visit(type_collector)

    param_types = type_collector.param_annotations
    return_types = type_collector.return_types
    variable_types = type_collector.variable_annotations

    # print(f"params: {param_types}, returns: {return_types}")
    # return f"params: {param_types}, returns: {return_types}"
    return param_types, return_types, variable_types


"""
def search_multiple_strings_in_file(file_name, list_of_strings):
    #Get line from the file along with line numbers, which contains any string from the list
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
    #Get line from the file along with line numbers, which contains any string from the list
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
"""


def search_key_value_in_snippet(file, list_of_strings) -> int:
    # Get line from the file along with line numbers, which contains any string from the list
    line_number = 0

    try:
        if len(list_of_strings[0]) > 1:
            strr = list_of_strings[0][-1]
        else:
            strr = "".join(list_of_strings[0])

        str2 = "".join(list_of_strings[1])

        # Read all lines in the file one by one
        for line in file.splitlines():
            line_number += 1
            # TODO: Add regex for edge cases

            l = line
            if strr in line and "".join(list_of_strings[1]) in line.replace(" ", "") and (':' in l or '->' in l):
                # If any string is found in line, then append that line along with line number in list
                return line_number, l.rstrip()
    except Exception as e:
        print('Error in search_key_value_in_snippet: ' + str(e))

    # Return list of tuples containing matched string, line numbers and lines where string is found
    return " ", " "


def search_line_number_param(file, dict):
    try:
        key_list = copy.deepcopy(list(dict.keys()))
        line_number = 0
        class_visited = set()
        method_visited = set()
        method_temp = ""

        for line in file.splitlines():
            line_number = line_number + 1
            if line_number == 147:
                xxx = 0
                xxx = 2

            list_temp = []
            for key in key_list:
                regex_temp = (re.escape(key[-1]) + "\s*:\s*" + re.escape(dict[key])).replace("[\\]", "[(.*?)\\]")

                key_temp = ""

                if len(key) > 2:
                    key_temp = key[-3]
                    if re.search("class\s*" + re.escape(key_temp) + "\s*:\s*", line):
                        class_visited.add(key[-3])

                    if re.search("def\s*" + re.escape(key[-2]) + "\s*", line):
                        # method_visited.add(key[-2])
                        method_temp = key[-2]

                if re.search(regex_temp,
                             line.replace(" ", "")) and key_temp in class_visited and key[-2] == method_temp:
                    key2 = tuple(tuple([line_number]) + key[2:])
                    dict[key2] = dict[key]
                    del dict[key]
                    list_temp.append(key)

            for key_temp in list_temp:
                key_list.remove(tuple(key_temp))

    except Exception as e:

        print('Error in search_key_value_in_snippet: ' + str(e))

    return


def search_line_number_param_new(file, dict):
    try:
        key_list = copy.deepcopy(list(dict.keys()))
        line_number = 0
        class_visited = set()
        method_visited = set()
        method_temp = ""

        for line in file.splitlines():
            line_number = line_number + 1
            if line_number == 147:
                xxx = 0
                xxx = 2

            list_temp = []
            for key in key_list:
                regex_temp = (re.escape(key[-1]) + "\s*:\s*" + re.escape(dict[key])).replace("[\\]", "[(.*?)\\]")

                key_temp = ""

                if len(key) > 2:
                    key_temp = key[-3]
                    if re.search("class\s*" + re.escape(key_temp) + "\s*:\s*", line):
                        class_visited.add(key[-3])

                    if re.search("def\s*" + re.escape(key[-2]) + "\s*", line):
                        # method_visited.add(key[-2])
                        method_temp = key[-2]

                if re.search(regex_temp,
                             line.replace(" ", "")) and key_temp in class_visited and key[-2] == method_temp:
                    key2 = tuple(tuple([line_number]) + key[2:])
                    dict[key2] = dict[key]
                    del dict[key]
                    list_temp.append(key)

            for key_temp in list_temp:
                key_list.remove(tuple(key_temp))

    except Exception as e:

        print('Error in search_key_value_in_snippet: ' + str(e))

    return


def search_line_number_return(file, dict):
    try:
        key_list = copy.deepcopy(list(dict.keys()))
        line_number = 0
        class_visited = set()
        method_temp = ""

        for line in file.splitlines():
            line_number = line_number + 1
            if line_number == 93:
                xxx = 0
                xxx = 2

            list_temp = []
            for key in key_list:
                annotation_regex = re.sub(r'\[(.*?)\]', '[(.*?)\\]', re.escape(dict[key]))
                regex_temp = (re.escape("->") + "\s*" + annotation_regex)

                key_temp = ""

                if len(key) == 2:
                    key_temp = key[-2]
                    if re.search("class\s*" + re.escape(key_temp) + "\(.*?\):\s*", line):
                        class_visited.add(key[-2])

                    if re.search("def\s*" + re.escape(key[-1]), line):
                        # method_visited.add(key[-1])
                        method_temp = key[-1]

                if re.search(regex_temp,
                             line.replace(" ", "")) and key_temp in class_visited and key[-1] == method_temp:
                    key2 = tuple(tuple([line_number]) + key[1:])
                    dict[key2] = dict[key]
                    del dict[key]
                    list_temp.append(key)

            for key_temp in list_temp:
                key_list.remove(tuple(key_temp))

    except Exception as e:

        print('Error in search_key_value_in_snippet: ' + str(e))

    return


def TypeAnnotationExtraction(repo_path, repo_name, commit, patch, url, statistics,  # lock, logging,
                             at_least_one_type_change, code_changes,
                             typeannotation_line_inserted, typeannotation_line_removed, typeannotation_line_changed,
                             list_line_added, list_line_removed, commit_year):
    code_changes_new = []

    line_type_annotation_added = []
    line_type_annotation_removed = []
    line_type_annotation_changed = []

    old_out = subprocess.Popen(
        ["git", "--git-dir", str(repo_path + repo_name) + '/.git', 'show',
         str(commit.hex + '^') + ":" + str(patch.delta.old_file.path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    old_stdout, old_stderr = old_out.communicate()

    if "fatal" in str(old_stdout):
        old_param_types = old_return_types = old_variable_types = {}
    else:
        try:
            old_param_types, old_return_types, old_variable_types = extract_from_snippet(
                str(old_stdout.decode('utf-8')))
        except:
            return

    new_out = subprocess.Popen(["git", "--git-dir", str(repo_path + repo_name) + '/.git', 'show',
                                str(commit.hex) + ":" + str(patch.delta.new_file.path)],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    new_stdout, new_stderr = new_out.communicate()

    if "fatal" in str(new_stdout):
        new_param_types = new_return_types = new_variable_types = {}
    else:
        try:
            new_param_types, new_return_types, new_variable_types = extract_from_snippet(
                str(new_stdout.decode('utf-8')))
        except:
            return

    try:
        old_line = old_code = new_line = new_code = ' '
        """
        pre_trasform = len(old_param_types)
        search_line_number_param(str(old_stdout.decode('utf-8')), old_param_types)

        if pre_trasform != len(old_param_types):
            print("Different size dict old_param_types", repo_path, commit)

        pre_trasform = len(new_param_types)
        search_line_number_param(str(new_stdout.decode('utf-8')), new_param_types)

        if pre_trasform != len(new_param_types):
            print("Different size dict new_param_types", repo_path, commit)

        pre_trasform = len(old_return_types)
        search_line_number_return(str(old_stdout.decode('utf-8')), old_return_types)

        if pre_trasform != len(old_return_types):
            print("Different size dict old_return_types", repo_path, commit)

        pre_trasform = len(new_return_types)
        search_line_number_return(str(new_stdout.decode('utf-8')), new_return_types)

        if pre_trasform != len(new_return_types):
            print("Different size dict old_return_types", repo_path, commit)
            
        """

        ################################################################
        ########  RETURN TYPE ANNOTATIONS                          #####
        ################################################################

        # Modify existing type annotation
        for key in old_return_types:
            if key in new_return_types:
                if old_return_types[key] != new_return_types[key]:

                    try:
                        old_line, old_code = search_key_value_in_snippet(str(old_stdout.decode('utf-8')),
                                                                         [key, old_return_types[key]])
                        new_line, new_code = search_key_value_in_snippet(str(new_stdout.decode('utf-8')),
                                                                         [key, new_return_types[key]])
                    except:
                        old_line = old_code = new_line = new_code = ' '

                    temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line,
                                      str(old_return_types[key]),
                                      str(patch.delta.new_file.path),
                                      new_line, str(new_return_types[key]))

                    # if temp not in code_changes_new:
                    code_changes_new.append(temp)

                    # lock.acquire()
                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    statistics.modify_existing_types += 1
                    # type_annotation_changed_this_commit += 1
                    line_type_annotation_changed.append(new_line)

                    if str(old_return_types[key] + ' -> ' + new_return_types[
                        key]).lower() not in statistics.typeChanged_dict:
                        statistics.typeChanged_dict[
                            str(old_return_types[key] + ' -> ' + new_return_types[key]).lower()] = 1
                    else:
                        statistics.typeChanged_dict[
                            str(old_return_types[key] + ' -> ' + new_return_types[key]).lower()] += 1
                    statistics.total_changed += 1
                    statistics.functionReturnsType_changed += 1
                    # list_line_added.add(key)
                    # list_line_removed.add(key)

                    # lock.release()

            # Remove type annotation
            else:
                for key_new in new_return_types:
                    try:
                        new_line, new_code = search_key_value_in_snippet(str(new_stdout.decode('utf-8')),
                                                                         [key_new, old_return_types[key]])

                        if (new_line != " "):
                            break
                    except:
                        old_line = old_code = new_line = new_code = ' '

                try:
                    old_line, old_code = search_key_value_in_snippet(str(old_stdout.decode('utf-8')),
                                                                     [key, old_return_types[key]])
                except:
                    old_line = old_code = new_line = new_code = ' '

                temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line,
                                  str(old_return_types[key]),
                                  str(patch.delta.new_file.path),
                                  '', '')

                # if temp not in code_changes_new:
                code_changes_new.append(temp)

                # lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.remove_types += 1
                # type_annotation_removed_this_commit += 1
                line_type_annotation_removed.append(old_line)

                if old_return_types[key].lower() not in statistics.typeRemoved_dict:
                    statistics.typeRemoved_dict[old_return_types[key].lower()] = 1
                else:
                    statistics.typeRemoved_dict[old_return_types[key].lower()] += 1
                statistics.total_removed += 1
                statistics.functionReturnsType_removed += 1
                # list_line_removed.add(key)
                # lock.release()

        # Insert type annotation
        for key in new_return_types:
            if key not in old_return_types:
                try:
                    new_line, new_code = search_key_value_in_snippet(str(new_stdout.decode('utf-8')),
                                                                     [key, new_return_types[key]])
                except:
                    old_line = old_code = new_line = new_code = ' '

                temp = CodeChange(url + str(new_line), commit_year, str(patch.delta.old_file.path), '', '',
                                  str(patch.delta.new_file.path),
                                  new_line, str(new_return_types[key]))

                # if temp not in code_changes_new:
                code_changes_new.append(temp)

                # lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.insert_types += 1
                # type_annotation_added_this_commit += 1
                line_type_annotation_added.append(new_line)

                if new_return_types[key].lower() not in statistics.typeAdded_dict:
                    statistics.typeAdded_dict[new_return_types[key].lower()] = 1
                else:
                    statistics.typeAdded_dict[new_return_types[key].lower()] += 1
                statistics.total_added += 1
                statistics.functionReturnsType_added += 1

                # list_line_added.add(key)
                # lock.release()

        ################################################################
        ########  ARGUMENTS TYPE ANNOTATIONS                       #####
        ################################################################

        # Modify existing type annotation
        for key in old_param_types:
            if key in new_param_types:
                if old_param_types[key] != new_param_types[key]:

                    try:
                        old_line, old_code = search_key_value_in_snippet(str(old_stdout.decode('utf-8')),
                                                                         [key, old_param_types[key]])
                        new_line, new_code = search_key_value_in_snippet(str(new_stdout.decode('utf-8')),
                                                                         [key, new_param_types[key]])
                    except:
                        old_line = old_code = new_line = new_code = ' '

                    temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line,
                                      str(old_param_types[key]),
                                      str(patch.delta.new_file.path),
                                      new_line, str(new_param_types[key]))

                    # if temp not in code_changes_new:
                    code_changes_new.append(temp)

                    # lock.acquire()
                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    statistics.modify_existing_types += 1
                    # type_annotation_changed_this_commit += 1
                    line_type_annotation_changed.append(old_line)

                    if str(old_param_types[key] + ' -> ' + new_param_types[
                        key]).lower() not in statistics.typeChanged_dict:
                        statistics.typeChanged_dict[
                            str(old_param_types[key] + ' -> ' + new_param_types[key]).lower()] = 1
                    else:
                        statistics.typeChanged_dict[
                            str(old_param_types[key] + ' -> ' + new_param_types[key]).lower()] += 1
                    statistics.total_changed += 1
                    statistics.functionArgsType_changed += 1

                    # list_line_added.add(key)
                    # list_line_removed.add(key)

                    # lock.release()

            # Remove type annotation
            else:
                try:
                    old_line, old_code = search_key_value_in_snippet(str(old_stdout.decode('utf-8')),
                                                                     [key, old_param_types[key]])
                except:
                    old_line = old_code = new_line = new_code = ' '

                temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line,
                                  str(old_param_types[key]),
                                  str(patch.delta.new_file.path),
                                  '', '')

                # if temp not in code_changes_new:
                code_changes_new.append(temp)

                # lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.remove_types += 1
                # type_annotation_removed_this_commit += 1
                line_type_annotation_removed.append(old_line)

                if old_param_types[key].lower() not in statistics.typeRemoved_dict:
                    statistics.typeRemoved_dict[old_param_types[key].lower()] = 1
                else:
                    statistics.typeRemoved_dict[old_param_types[key].lower()] += 1
                statistics.total_removed += 1
                statistics.functionArgsType_removed += 1

                # list_line_removed.add(key)
                # lock.release()

        # Insert type annotation
        for key in new_param_types:
            if key not in old_param_types:
                try:
                    new_line, new_code = search_key_value_in_snippet(str(new_stdout.decode('utf-8')),
                                                                     [key, new_param_types[key]])
                except:
                    old_line = old_code = new_line = new_code = ' '

                temp = CodeChange(url + str(new_line), commit_year, str(patch.delta.old_file.path), '', '',
                                  str(patch.delta.new_file.path),
                                  new_line, str(new_param_types[key]))

                # if temp not in code_changes_new:
                code_changes_new.append(temp)

                # lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.insert_types += 1
                # type_annotation_added_this_commit += 1
                line_type_annotation_added.append(new_line)

                if new_param_types[key].lower() not in statistics.typeAdded_dict:
                    statistics.typeAdded_dict[new_param_types[key].lower()] = 1
                else:
                    statistics.typeAdded_dict[new_param_types[key].lower()] += 1
                statistics.total_added += 1
                statistics.functionArgsType_added += 1

                # list_line_added.add(key)
                # lock.release()

        ################################################################
        ########  VARIABLE TYPE ANNOTATIONS                        #####
        ################################################################

        # Modify existing type annotation
        for key in old_variable_types:
            if key in new_variable_types:
                if old_variable_types[key] != new_variable_types[key]:
                    try:
                        old_line, old_code = search_key_value_in_snippet(
                            str(new_stdout.decode('utf-8')),
                            [key, old_variable_types[key]])
                        new_line, new_code = search_key_value_in_snippet(
                            str(new_stdout.decode('utf-8')),
                            [key, new_variable_types[key]])
                    except:
                        old_line = old_code = new_line = new_code = ' '

                    temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line,
                                      str(old_variable_types[key]),
                                      str(patch.delta.new_file.path),
                                      new_line, str(new_variable_types[key]))

                    # if temp not in code_changes_new:
                    code_changes_new.append(temp)

                    # lock.acquire()
                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    statistics.modify_existing_types += 1
                    # type_annotation_changed_this_commit += 1
                    line_type_annotation_changed.append(old_line)

                    if str(old_variable_types[key] + ' -> ' + new_variable_types[
                        key]).lower() not in statistics.typeChanged_dict:
                        statistics.typeChanged_dict[
                            str(old_variable_types[key] + ' -> ' + new_variable_types[key]).lower()] = 1
                    else:
                        statistics.typeChanged_dict[
                            str(old_variable_types[key] + ' -> ' + new_variable_types[key]).lower()] += 1
                    statistics.total_changed += 1
                    statistics.variableType_changed += 1

                    # list_line_added.add(key)
                    # list_line_removed.add(key)

                    # lock.release()

            # Remove type annotation
            else:
                try:
                    old_line, old_code = search_key_value_in_snippet(
                        str(new_stdout.decode('utf-8')),
                        [key, old_variable_types[key]])
                except:
                    old_line = old_code = new_line = new_code = ' '

                if key in old_variable_types:
                    temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line,
                                      str(old_variable_types[key]),
                                      str(patch.delta.new_file.path),
                                      '', '')

                    # if temp not in code_changes_new:
                    code_changes_new.append(temp)

                    # lock.acquire()
                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    statistics.remove_types += 1
                    # type_annotation_removed_this_commit += 1
                    line_type_annotation_removed.append(old_line)

                    if old_variable_types[key].lower() not in statistics.typeRemoved_dict:
                        statistics.typeRemoved_dict[old_variable_types[key].lower()] = 1
                    else:
                        statistics.typeRemoved_dict[old_variable_types[key].lower()] += 1
                    statistics.total_removed += 1
                    statistics.variableType_removed += 1

                    # list_line_removed.add(key)
                    # lock.release()

        # Insert type annotation
        for key in new_variable_types:
            if key not in old_variable_types:
                try:
                    new_line, new_code = search_key_value_in_snippet(
                        str(new_stdout.decode('utf-8')),
                        [key, new_variable_types[key]])
                except:
                    old_line = old_code = new_line = new_code = ' '

                temp = CodeChange(url + str(new_line), commit_year, str(patch.delta.old_file.path), '', '',
                                  str(patch.delta.new_file.path),
                                  new_line, str(new_variable_types[key]))

                # if temp not in code_changes_new:
                code_changes_new.append(temp)

                # lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.insert_types += 1
                # type_annotation_added_this_commit += 1
                line_type_annotation_added.append(new_line)

                if new_variable_types[key].lower() not in statistics.typeAdded_dict:
                    statistics.typeAdded_dict[new_variable_types[key].lower()] = 1
                else:
                    statistics.typeAdded_dict[new_variable_types[key].lower()] += 1
                statistics.total_added += 1
                statistics.variableType_added += 1

                # list_line_added.add(key)
                # lock.release()
    except Exception as e:
        print('Error changeExtraction:', repo_path, commit, str(e))
        # print('Repository', repo_path, 'commit', commit, 'with old line', str(old_stdout))

    # lock.acquire()
    if len(line_type_annotation_added) > 0:
        # statistics.list_typeAnnotation_added_per_commit.append(type_annotation_added_this_commit)
        typeannotation_line_inserted[0] += len(set(line_type_annotation_added))
        list_line_added[0] += len(set(line_type_annotation_added))

    if len(line_type_annotation_removed) > 0:
        # statistics.list_typeAnnotation_removed_per_commit.append(type_annotation_removed_this_commit)
        typeannotation_line_removed[0] += len(set(line_type_annotation_removed))
        list_line_removed[0] += len(set(line_type_annotation_removed))

    if len(line_type_annotation_changed) > 0:
        # statistics.list_typeAnnotation_changed_per_commit.append(type_annotation_changed_this_commit)
        typeannotation_line_inserted[0] += len(set(line_type_annotation_changed))
        typeannotation_line_removed[0] += len(set(line_type_annotation_changed))
        typeannotation_line_changed[0] += len(set(line_type_annotation_changed))

        list_line_added[0] += len(set(line_type_annotation_added))
        list_line_removed[0] += len(set(line_type_annotation_removed))

    if len(code_changes_new) > 0:
        # statistics.commits_with_typeChanges += 1
        # tot_this_repo_commit_with_annotations[0] += 1
        # commit_with_annotations_this_repo[0] += 1
        at_least_one_type_change[0] += 1

        code_changes += code_changes_new

    # lock.release()


def hunk_extraction(hunk):
    old_hunk = ""
    new_hunk = ""

    for line_data in hunk.lines:
        if line_data.old_lineno > 0:
            old_hunk += line_data.content

        if line_data.new_lineno > 0:
            new_hunk += line_data.content

    return old_hunk, new_hunk


def TypeAnnotationExtractionNewNew(repo_path, repo_name, commit, patch, url, statistics,  # lock, logging,
                                   at_least_one_type_change, code_changes,
                                   typeannotation_line_inserted, typeannotation_line_removed,
                                   typeannotation_line_changed,
                                   list_line_added, list_line_removed, commit_year):
    code_changes_new = []

    line_type_annotation_added = []
    line_type_annotation_removed = []
    line_type_annotation_changed = []

    for hunk in patch.hunks:
        old_hunk, new_hunk = hunk_extraction(hunk)
        old_param_types, old_return_types, old_variable_types = extract_from_snippet(
            old_hunk)

    old_out = subprocess.Popen(
        ["git", "--git-dir", str(repo_path + repo_name) + '/.git', 'show',
         str(commit.hex + '^') + ":" + str(patch.delta.old_file.path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    old_stdout, old_stderr = old_out.communicate()

    if "fatal" in str(old_stdout):
        old_param_types = old_return_types = old_variable_types = {}
    else:
        try:
            old_param_types, old_return_types, old_variable_types = extract_from_snippet(
                str(old_stdout.decode('utf-8')))
        except:
            return

    new_out = subprocess.Popen(["git", "--git-dir", str(repo_path + repo_name) + '/.git', 'show',
                                str(commit.hex) + ":" + str(patch.delta.new_file.path)],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    new_stdout, new_stderr = new_out.communicate()

    if "fatal" in str(new_stdout):
        new_param_types = new_return_types = new_variable_types = {}
    else:
        try:
            new_param_types, new_return_types, new_variable_types = extract_from_snippet(
                str(new_stdout.decode('utf-8')))
        except:
            return

    try:
        old_line = old_code = new_line = new_code = ' '
        """
        pre_trasform = len(old_param_types)
        search_line_number_param(str(old_stdout.decode('utf-8')), old_param_types)

        if pre_trasform != len(old_param_types):
            print("Different size dict old_param_types", repo_path, commit)

        pre_trasform = len(new_param_types)
        search_line_number_param(str(new_stdout.decode('utf-8')), new_param_types)

        if pre_trasform != len(new_param_types):
            print("Different size dict new_param_types", repo_path, commit)

        pre_trasform = len(old_return_types)
        search_line_number_return(str(old_stdout.decode('utf-8')), old_return_types)

        if pre_trasform != len(old_return_types):
            print("Different size dict old_return_types", repo_path, commit)

        pre_trasform = len(new_return_types)
        search_line_number_return(str(new_stdout.decode('utf-8')), new_return_types)

        if pre_trasform != len(new_return_types):
            print("Different size dict old_return_types", repo_path, commit)

        """

        ################################################################
        ########  RETURN TYPE ANNOTATIONS                          #####
        ################################################################

        # Modify existing type annotation
        for key in old_return_types:
            if key in new_return_types:
                if old_return_types[key] != new_return_types[key]:

                    try:
                        old_line, old_code = search_key_value_in_snippet(str(old_stdout.decode('utf-8')),
                                                                         [key, old_return_types[key]])
                        new_line, new_code = search_key_value_in_snippet(str(new_stdout.decode('utf-8')),
                                                                         [key, new_return_types[key]])
                    except:
                        old_line = old_code = new_line = new_code = ' '

                    temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line,
                                      str(old_return_types[key]),
                                      str(patch.delta.new_file.path),
                                      new_line, str(new_return_types[key]))

                    # if temp not in code_changes_new:
                    code_changes_new.append(temp)

                    # lock.acquire()
                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    statistics.modify_existing_types += 1
                    # type_annotation_changed_this_commit += 1
                    line_type_annotation_changed.append(new_line)

                    if str(old_return_types[key] + ' -> ' + new_return_types[
                        key]).lower() not in statistics.typeChanged_dict:
                        statistics.typeChanged_dict[
                            str(old_return_types[key] + ' -> ' + new_return_types[key]).lower()] = 1
                    else:
                        statistics.typeChanged_dict[
                            str(old_return_types[key] + ' -> ' + new_return_types[key]).lower()] += 1
                    statistics.total_changed += 1
                    statistics.functionReturnsType_changed += 1
                    # list_line_added.add(key)
                    # list_line_removed.add(key)

                    # lock.release()

            # Remove type annotation
            else:
                for key_new in new_return_types:
                    try:
                        new_line, new_code = search_key_value_in_snippet(str(new_stdout.decode('utf-8')),
                                                                         [key_new, old_return_types[key]])

                        if (new_line != " "):
                            break
                    except:
                        old_line = old_code = new_line = new_code = ' '

                try:
                    old_line, old_code = search_key_value_in_snippet(str(old_stdout.decode('utf-8')),
                                                                     [key, old_return_types[key]])
                except:
                    old_line = old_code = new_line = new_code = ' '

                temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line,
                                  str(old_return_types[key]),
                                  str(patch.delta.new_file.path),
                                  '', '')

                # if temp not in code_changes_new:
                code_changes_new.append(temp)

                # lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.remove_types += 1
                # type_annotation_removed_this_commit += 1
                line_type_annotation_removed.append(old_line)

                if old_return_types[key].lower() not in statistics.typeRemoved_dict:
                    statistics.typeRemoved_dict[old_return_types[key].lower()] = 1
                else:
                    statistics.typeRemoved_dict[old_return_types[key].lower()] += 1
                statistics.total_removed += 1
                statistics.functionReturnsType_removed += 1
                # list_line_removed.add(key)
                # lock.release()

        # Insert type annotation
        for key in new_return_types:
            if key not in old_return_types:
                try:
                    new_line, new_code = search_key_value_in_snippet(str(new_stdout.decode('utf-8')),
                                                                     [key, new_return_types[key]])
                except:
                    old_line = old_code = new_line = new_code = ' '

                temp = CodeChange(url + str(new_line), commit_year, str(patch.delta.old_file.path), '', '',
                                  str(patch.delta.new_file.path),
                                  new_line, str(new_return_types[key]))

                # if temp not in code_changes_new:
                code_changes_new.append(temp)

                # lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.insert_types += 1
                # type_annotation_added_this_commit += 1
                line_type_annotation_added.append(new_line)

                if new_return_types[key].lower() not in statistics.typeAdded_dict:
                    statistics.typeAdded_dict[new_return_types[key].lower()] = 1
                else:
                    statistics.typeAdded_dict[new_return_types[key].lower()] += 1
                statistics.total_added += 1
                statistics.functionReturnsType_added += 1

                # list_line_added.add(key)
                # lock.release()

        ################################################################
        ########  ARGUMENTS TYPE ANNOTATIONS                       #####
        ################################################################

        # Modify existing type annotation
        for key in old_param_types:
            if key in new_param_types:
                if old_param_types[key] != new_param_types[key]:

                    try:
                        old_line, old_code = search_key_value_in_snippet(str(old_stdout.decode('utf-8')),
                                                                         [key, old_param_types[key]])
                        new_line, new_code = search_key_value_in_snippet(str(new_stdout.decode('utf-8')),
                                                                         [key, new_param_types[key]])
                    except:
                        old_line = old_code = new_line = new_code = ' '

                    temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line,
                                      str(old_param_types[key]),
                                      str(patch.delta.new_file.path),
                                      new_line, str(new_param_types[key]))

                    # if temp not in code_changes_new:
                    code_changes_new.append(temp)

                    # lock.acquire()
                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    statistics.modify_existing_types += 1
                    # type_annotation_changed_this_commit += 1
                    line_type_annotation_changed.append(old_line)

                    if str(old_param_types[key] + ' -> ' + new_param_types[
                        key]).lower() not in statistics.typeChanged_dict:
                        statistics.typeChanged_dict[
                            str(old_param_types[key] + ' -> ' + new_param_types[key]).lower()] = 1
                    else:
                        statistics.typeChanged_dict[
                            str(old_param_types[key] + ' -> ' + new_param_types[key]).lower()] += 1
                    statistics.total_changed += 1
                    statistics.functionArgsType_changed += 1

                    # list_line_added.add(key)
                    # list_line_removed.add(key)

                    # lock.release()

            # Remove type annotation
            else:
                try:
                    old_line, old_code = search_key_value_in_snippet(str(old_stdout.decode('utf-8')),
                                                                     [key, old_param_types[key]])
                except:
                    old_line = old_code = new_line = new_code = ' '

                temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line,
                                  str(old_param_types[key]),
                                  str(patch.delta.new_file.path),
                                  '', '')

                # if temp not in code_changes_new:
                code_changes_new.append(temp)

                # lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.remove_types += 1
                # type_annotation_removed_this_commit += 1
                line_type_annotation_removed.append(old_line)

                if old_param_types[key].lower() not in statistics.typeRemoved_dict:
                    statistics.typeRemoved_dict[old_param_types[key].lower()] = 1
                else:
                    statistics.typeRemoved_dict[old_param_types[key].lower()] += 1
                statistics.total_removed += 1
                statistics.functionArgsType_removed += 1

                # list_line_removed.add(key)
                # lock.release()

        # Insert type annotation
        for key in new_param_types:
            if key not in old_param_types:
                try:
                    new_line, new_code = search_key_value_in_snippet(str(new_stdout.decode('utf-8')),
                                                                     [key, new_param_types[key]])
                except:
                    old_line = old_code = new_line = new_code = ' '

                temp = CodeChange(url + str(new_line), commit_year, str(patch.delta.old_file.path), '', '',
                                  str(patch.delta.new_file.path),
                                  new_line, str(new_param_types[key]))

                # if temp not in code_changes_new:
                code_changes_new.append(temp)

                # lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.insert_types += 1
                # type_annotation_added_this_commit += 1
                line_type_annotation_added.append(new_line)

                if new_param_types[key].lower() not in statistics.typeAdded_dict:
                    statistics.typeAdded_dict[new_param_types[key].lower()] = 1
                else:
                    statistics.typeAdded_dict[new_param_types[key].lower()] += 1
                statistics.total_added += 1
                statistics.functionArgsType_added += 1

                # list_line_added.add(key)
                # lock.release()

        ################################################################
        ########  VARIABLE TYPE ANNOTATIONS                        #####
        ################################################################

        # Modify existing type annotation
        for key in old_variable_types:
            if key in new_variable_types:
                if old_variable_types[key] != new_variable_types[key]:
                    try:
                        old_line, old_code = search_key_value_in_snippet(
                            str(new_stdout.decode('utf-8')),
                            [key, old_variable_types[key]])
                        new_line, new_code = search_key_value_in_snippet(
                            str(new_stdout.decode('utf-8')),
                            [key, new_variable_types[key]])
                    except:
                        old_line = old_code = new_line = new_code = ' '

                    temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line,
                                      str(old_variable_types[key]),
                                      str(patch.delta.new_file.path),
                                      new_line, str(new_variable_types[key]))

                    # if temp not in code_changes_new:
                    code_changes_new.append(temp)

                    # lock.acquire()
                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    statistics.modify_existing_types += 1
                    # type_annotation_changed_this_commit += 1
                    line_type_annotation_changed.append(old_line)

                    if str(old_variable_types[key] + ' -> ' + new_variable_types[
                        key]).lower() not in statistics.typeChanged_dict:
                        statistics.typeChanged_dict[
                            str(old_variable_types[key] + ' -> ' + new_variable_types[key]).lower()] = 1
                    else:
                        statistics.typeChanged_dict[
                            str(old_variable_types[key] + ' -> ' + new_variable_types[key]).lower()] += 1
                    statistics.total_changed += 1
                    statistics.variableType_changed += 1

                    # list_line_added.add(key)
                    # list_line_removed.add(key)

                    # lock.release()

            # Remove type annotation
            else:
                try:
                    old_line, old_code = search_key_value_in_snippet(
                        str(new_stdout.decode('utf-8')),
                        [key, old_variable_types[key]])
                except:
                    old_line = old_code = new_line = new_code = ' '

                if key in old_variable_types:
                    temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line,
                                      str(old_variable_types[key]),
                                      str(patch.delta.new_file.path),
                                      '', '')

                    # if temp not in code_changes_new:
                    code_changes_new.append(temp)

                    # lock.acquire()
                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    statistics.remove_types += 1
                    # type_annotation_removed_this_commit += 1
                    line_type_annotation_removed.append(old_line)

                    if old_variable_types[key].lower() not in statistics.typeRemoved_dict:
                        statistics.typeRemoved_dict[old_variable_types[key].lower()] = 1
                    else:
                        statistics.typeRemoved_dict[old_variable_types[key].lower()] += 1
                    statistics.total_removed += 1
                    statistics.variableType_removed += 1

                    # list_line_removed.add(key)
                    # lock.release()

        # Insert type annotation
        for key in new_variable_types:
            if key not in old_variable_types:
                try:
                    new_line, new_code = search_key_value_in_snippet(
                        str(new_stdout.decode('utf-8')),
                        [key, new_variable_types[key]])
                except:
                    old_line = old_code = new_line = new_code = ' '

                temp = CodeChange(url + str(new_line), commit_year, str(patch.delta.old_file.path), '', '',
                                  str(patch.delta.new_file.path),
                                  new_line, str(new_variable_types[key]))

                # if temp not in code_changes_new:
                code_changes_new.append(temp)

                # lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.insert_types += 1
                # type_annotation_added_this_commit += 1
                line_type_annotation_added.append(new_line)

                if new_variable_types[key].lower() not in statistics.typeAdded_dict:
                    statistics.typeAdded_dict[new_variable_types[key].lower()] = 1
                else:
                    statistics.typeAdded_dict[new_variable_types[key].lower()] += 1
                statistics.total_added += 1
                statistics.variableType_added += 1

                # list_line_added.add(key)
                # lock.release()
    except Exception as e:
        print('Error changeExtraction:', repo_path, commit, str(e))
        # print('Repository', repo_path, 'commit', commit, 'with old line', str(old_stdout))

    # lock.acquire()
    if len(line_type_annotation_added) > 0:
        # statistics.list_typeAnnotation_added_per_commit.append(type_annotation_added_this_commit)
        typeannotation_line_inserted[0] += len(set(line_type_annotation_added))
        list_line_added[0] += len(set(line_type_annotation_added))

    if len(line_type_annotation_removed) > 0:
        # statistics.list_typeAnnotation_removed_per_commit.append(type_annotation_removed_this_commit)
        typeannotation_line_removed[0] += len(set(line_type_annotation_removed))
        list_line_removed[0] += len(set(line_type_annotation_removed))

    if len(line_type_annotation_changed) > 0:
        # statistics.list_typeAnnotation_changed_per_commit.append(type_annotation_changed_this_commit)
        typeannotation_line_inserted[0] += len(set(line_type_annotation_changed))
        typeannotation_line_removed[0] += len(set(line_type_annotation_changed))
        typeannotation_line_changed[0] += len(set(line_type_annotation_changed))

        list_line_added[0] += len(set(line_type_annotation_added))
        list_line_removed[0] += len(set(line_type_annotation_removed))

    if len(code_changes_new) > 0:
        # statistics.commits_with_typeChanges += 1
        # tot_this_repo_commit_with_annotations[0] += 1
        # commit_with_annotations_this_repo[0] += 1
        at_least_one_type_change[0] += 1

        code_changes += code_changes_new

    # lock.release()


def TypeAnnotationExtractionNew(repo_path, repo_name, commit, patch, url, statistics,  # lock, logging,
                                at_least_one_type_change, code_changes,
                                typeannotation_line_inserted, typeannotation_line_removed, typeannotation_line_changed,
                                list_line_added, list_line_removed, commit_year):
    code_changes_new = []

    line_type_annotation_added = []
    line_type_annotation_removed = []
    line_type_annotation_changed = []

    old_out = subprocess.Popen(
        ["git", "--git-dir", str(repo_path + repo_name) + '/.git', 'show',
         str(commit.hex + '^') + ":" + str(patch.delta.old_file.path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    old_stdout, old_stderr = old_out.communicate()

    if "fatal" in str(old_stdout):
        old_param_types = old_return_types = old_variable_types = {}
    else:
        try:
            old_param_types, old_return_types, old_variable_types = extract_from_snippet(
                str(old_stdout.decode('utf-8')))
        except:
            return

    new_out = subprocess.Popen(["git", "--git-dir", str(repo_path + repo_name) + '/.git', 'show',
                                str(commit.hex) + ":" + str(patch.delta.new_file.path)],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    new_stdout, new_stderr = new_out.communicate()

    if "fatal" in str(new_stdout):
        new_param_types = new_return_types = new_variable_types = {}
    else:
        try:
            new_param_types, new_return_types, new_variable_types = extract_from_snippet(
                str(new_stdout.decode('utf-8')))
        except:
            return

    try:
        old_line = old_code = new_line = new_code = ' '

        pre_trasform = len(old_param_types)
        search_line_number_param(str(old_stdout.decode('utf-8')), old_param_types)

        if pre_trasform != len(old_param_types):
            print("Different size dict old_param_types", repo_path, commit)

        pre_trasform = len(new_param_types)
        search_line_number_param(str(new_stdout.decode('utf-8')), new_param_types)

        if pre_trasform != len(new_param_types):
            print("Different size dict new_param_types", repo_path, commit)

        pre_trasform = len(old_return_types)
        search_line_number_return(str(old_stdout.decode('utf-8')), old_return_types)

        if pre_trasform != len(old_return_types):
            print("Different size dict old_return_types", repo_path, commit)

        pre_trasform = len(new_return_types)
        search_line_number_return(str(new_stdout.decode('utf-8')), new_return_types)

        if pre_trasform != len(new_return_types):
            print("Different size dict old_return_types", repo_path, commit)

        ################################################################
        ########  RETURN TYPE ANNOTATIONS                          #####
        ################################################################

        # Modify existing type annotation
        for key in old_return_types:
            if key in new_return_types:
                if old_return_types[key] != new_return_types[key]:

                    try:
                        old_line, old_code, new_line, new_code = key[-2]

                    except:
                        try:
                            old_line, old_code = search_key_value_in_snippet(str(old_stdout.decode('utf-8')),
                                                                             [key, old_return_types[key]])
                            new_line, new_code = search_key_value_in_snippet(str(new_stdout.decode('utf-8')),
                                                                             [key, new_return_types[key]])
                        except:
                            old_line = old_code = new_line = new_code = ''

                    temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line,
                                      str(old_return_types[key]),
                                      str(patch.delta.new_file.path),
                                      new_line, str(new_return_types[key]))

                    # if temp not in code_changes_new:
                    code_changes_new.append(temp)

                    # lock.acquire()
                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    statistics.modify_existing_types += 1
                    # type_annotation_changed_this_commit += 1
                    line_type_annotation_changed.append(new_line)

                    if str(old_return_types[key] + ' -> ' + new_return_types[
                        key]).lower() not in statistics.typeChanged_dict:
                        statistics.typeChanged_dict[
                            str(old_return_types[key] + ' -> ' + new_return_types[key]).lower()] = 1
                    else:
                        statistics.typeChanged_dict[
                            str(old_return_types[key] + ' -> ' + new_return_types[key]).lower()] += 1
                    statistics.total_changed += 1
                    statistics.functionReturnsType_changed += 1
                    # list_line_added.add(key)
                    # list_line_removed.add(key)

                    # lock.release()

            # Remove type annotation
            else:

                try:
                    old_line, old_code, new_line, new_code = key[-2]
                except:
                    try:
                        old_line, old_code = search_key_value_in_snippet(str(old_stdout.decode('utf-8')),
                                                                         [key, old_return_types[key]])
                    except:
                        old_line = old_code = new_line = new_code = ''

                temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line,
                                  str(old_return_types[key]),
                                  str(patch.delta.new_file.path),
                                  '', '')

                # if temp not in code_changes_new:
                code_changes_new.append(temp)

                # lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.remove_types += 1
                # type_annotation_removed_this_commit += 1
                line_type_annotation_removed.append(old_line)

                if old_return_types[key].lower() not in statistics.typeRemoved_dict:
                    statistics.typeRemoved_dict[old_return_types[key].lower()] = 1
                else:
                    statistics.typeRemoved_dict[old_return_types[key].lower()] += 1
                statistics.total_removed += 1
                statistics.functionReturnsType_removed += 1
                # list_line_removed.add(key)
                # lock.release()

        # Insert type annotation
        for key in new_return_types:
            if key not in old_return_types:
                try:
                    old_line, old_code, new_line, new_code = key[-2]
                except:
                    try:
                        new_line, new_code = search_key_value_in_snippet(str(new_stdout.decode('utf-8')),
                                                                         [key, new_return_types[key]])
                    except:
                        old_line = old_code = new_line = new_code = ''

                temp = CodeChange(url + str(new_line), commit_year, str(patch.delta.old_file.path), '', '',
                                  str(patch.delta.new_file.path),
                                  new_line, str(new_return_types[key]))

                # if temp not in code_changes_new:
                code_changes_new.append(temp)

                # lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.insert_types += 1
                # type_annotation_added_this_commit += 1
                line_type_annotation_added.append(new_line)

                if new_return_types[key].lower() not in statistics.typeAdded_dict:
                    statistics.typeAdded_dict[new_return_types[key].lower()] = 1
                else:
                    statistics.typeAdded_dict[new_return_types[key].lower()] += 1
                statistics.total_added += 1
                statistics.functionReturnsType_added += 1

                # list_line_added.add(key)
                # lock.release()

        ################################################################
        ########  ARGUMENTS TYPE ANNOTATIONS                       #####
        ################################################################

        # Modify existing type annotation
        for key in old_param_types:
            if key in new_param_types:
                if old_param_types[key] != new_param_types[key]:

                    try:
                        old_line, old_code, new_line, new_code = key[-2]
                    except:
                        try:
                            old_line, old_code = search_key_value_in_snippet(str(old_stdout.decode('utf-8')),
                                                                             [key, old_return_types[key]])
                            new_line, new_code = search_key_value_in_snippet(str(new_stdout.decode('utf-8')),
                                                                             [key, new_return_types[key]])
                        except:
                            old_line = old_code = new_line = new_code = ''

                    temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line,
                                      str(old_param_types[key]),
                                      str(patch.delta.new_file.path),
                                      new_line, str(new_param_types[key]))

                    # if temp not in code_changes_new:
                    code_changes_new.append(temp)

                    # lock.acquire()
                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    statistics.modify_existing_types += 1
                    # type_annotation_changed_this_commit += 1
                    line_type_annotation_changed.append(old_line)

                    if str(old_param_types[key] + ' -> ' + new_param_types[
                        key]).lower() not in statistics.typeChanged_dict:
                        statistics.typeChanged_dict[
                            str(old_param_types[key] + ' -> ' + new_param_types[key]).lower()] = 1
                    else:
                        statistics.typeChanged_dict[
                            str(old_param_types[key] + ' -> ' + new_param_types[key]).lower()] += 1
                    statistics.total_changed += 1
                    statistics.functionArgsType_changed += 1

                    # list_line_added.add(key)
                    # list_line_removed.add(key)

                    # lock.release()

            # Remove type annotation
            else:
                try:
                    old_line, old_code, new_line, new_code = key[-2]
                except:
                    try:
                        old_line, old_code = search_key_value_in_snippet(str(old_stdout.decode('utf-8')),
                                                                         [key, old_return_types[key]])
                    except:
                        old_line = old_code = new_line = new_code = ''

                temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line,
                                  str(old_param_types[key]),
                                  str(patch.delta.new_file.path),
                                  '', '')

                # if temp not in code_changes_new:
                code_changes_new.append(temp)

                # lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.remove_types += 1
                # type_annotation_removed_this_commit += 1
                line_type_annotation_removed.append(old_line)

                if old_param_types[key].lower() not in statistics.typeRemoved_dict:
                    statistics.typeRemoved_dict[old_param_types[key].lower()] = 1
                else:
                    statistics.typeRemoved_dict[old_param_types[key].lower()] += 1
                statistics.total_removed += 1
                statistics.functionArgsType_removed += 1

                # list_line_removed.add(key)
                # lock.release()

        # Insert type annotation
        for key in new_param_types:
            if key not in old_param_types:
                try:
                    old_line, old_code, new_line, new_code = key[-2]
                except:
                    try:
                        new_line, new_code = search_key_value_in_snippet(str(new_stdout.decode('utf-8')),
                                                                         [key, new_return_types[key]])
                    except:
                        old_line = old_code = new_line = new_code = ''

                temp = CodeChange(url + str(new_line), commit_year, str(patch.delta.old_file.path), '', '',
                                  str(patch.delta.new_file.path),
                                  new_line, str(new_param_types[key]))

                # if temp not in code_changes_new:
                code_changes_new.append(temp)

                # lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.insert_types += 1
                # type_annotation_added_this_commit += 1
                line_type_annotation_added.append(new_line)

                if new_param_types[key].lower() not in statistics.typeAdded_dict:
                    statistics.typeAdded_dict[new_param_types[key].lower()] = 1
                else:
                    statistics.typeAdded_dict[new_param_types[key].lower()] += 1
                statistics.total_added += 1
                statistics.functionArgsType_added += 1

                # list_line_added.add(key)
                # lock.release()

        ################################################################
        ########  VARIABLE TYPE ANNOTATIONS                        #####
        ################################################################

        # Modify existing type annotation
        for key in old_variable_types:
            if key in new_variable_types:
                if old_variable_types[key] != new_variable_types[key]:
                    try:
                        old_line, old_code = search_key_value_in_snippet(
                            str(new_stdout.decode('utf-8')),
                            [key, old_variable_types[key]])
                        new_line, new_code = search_key_value_in_snippet(
                            str(new_stdout.decode('utf-8')),
                            [key, new_variable_types[key]])
                    except:
                        old_line = old_code = new_line = new_code = ' '

                    temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line,
                                      str(old_variable_types[key]),
                                      str(patch.delta.new_file.path),
                                      new_line, str(new_variable_types[key]))

                    # if temp not in code_changes_new:
                    code_changes_new.append(temp)

                    # lock.acquire()
                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    statistics.modify_existing_types += 1
                    # type_annotation_changed_this_commit += 1
                    line_type_annotation_changed.append(old_line)

                    if str(old_variable_types[key] + ' -> ' + new_variable_types[
                        key]).lower() not in statistics.typeChanged_dict:
                        statistics.typeChanged_dict[
                            str(old_variable_types[key] + ' -> ' + new_variable_types[key]).lower()] = 1
                    else:
                        statistics.typeChanged_dict[
                            str(old_variable_types[key] + ' -> ' + new_variable_types[key]).lower()] += 1
                    statistics.total_changed += 1
                    statistics.variableType_changed += 1

                    # list_line_added.add(key)
                    # list_line_removed.add(key)

                    # lock.release()

            # Remove type annotation
            else:
                try:
                    old_line, old_code = search_key_value_in_snippet(
                        str(new_stdout.decode('utf-8')),
                        [key, old_variable_types[key]])
                except:
                    old_line = old_code = new_line = new_code = ' '

                if key in old_variable_types:
                    temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line,
                                      str(old_variable_types[key]),
                                      str(patch.delta.new_file.path),
                                      '', '')

                    # if temp not in code_changes_new:
                    code_changes_new.append(temp)

                    # lock.acquire()
                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    statistics.remove_types += 1
                    # type_annotation_removed_this_commit += 1
                    line_type_annotation_removed.append(old_line)

                    if old_variable_types[key].lower() not in statistics.typeRemoved_dict:
                        statistics.typeRemoved_dict[old_variable_types[key].lower()] = 1
                    else:
                        statistics.typeRemoved_dict[old_variable_types[key].lower()] += 1
                    statistics.total_removed += 1
                    statistics.variableType_removed += 1

                    # list_line_removed.add(key)
                    # lock.release()

        # Insert type annotation
        for key in new_variable_types:
            if key not in old_variable_types:
                try:
                    new_line, new_code = search_key_value_in_snippet(
                        str(new_stdout.decode('utf-8')),
                        [key, new_variable_types[key]])
                except:
                    old_line = old_code = new_line = new_code = ' '

                temp = CodeChange(url + str(new_line), commit_year, str(patch.delta.old_file.path), '', '',
                                  str(patch.delta.new_file.path),
                                  new_line, str(new_variable_types[key]))

                # if temp not in code_changes_new:
                code_changes_new.append(temp)

                # lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.insert_types += 1
                # type_annotation_added_this_commit += 1
                line_type_annotation_added.append(new_line)

                if new_variable_types[key].lower() not in statistics.typeAdded_dict:
                    statistics.typeAdded_dict[new_variable_types[key].lower()] = 1
                else:
                    statistics.typeAdded_dict[new_variable_types[key].lower()] += 1
                statistics.total_added += 1
                statistics.variableType_added += 1

                # list_line_added.add(key)
                # lock.release()
    except Exception as e:
        print('Error changeExtraction:', repo_path, commit, str(e))
        # print('Repository', repo_path, 'commit', commit, 'with old line', str(old_stdout))

    # lock.acquire()
    if len(line_type_annotation_added) > 0:
        # statistics.list_typeAnnotation_added_per_commit.append(type_annotation_added_this_commit)
        typeannotation_line_inserted[0] += len(set(line_type_annotation_added))
        list_line_added[0] += len(set(line_type_annotation_added))

    if len(line_type_annotation_removed) > 0:
        # statistics.list_typeAnnotation_removed_per_commit.append(type_annotation_removed_this_commit)
        typeannotation_line_removed[0] += len(set(line_type_annotation_removed))
        list_line_removed[0] += len(set(line_type_annotation_removed))

    if len(line_type_annotation_changed) > 0:
        # statistics.list_typeAnnotation_changed_per_commit.append(type_annotation_changed_this_commit)
        typeannotation_line_inserted[0] += len(set(line_type_annotation_changed))
        typeannotation_line_removed[0] += len(set(line_type_annotation_changed))
        typeannotation_line_changed[0] += len(set(line_type_annotation_changed))

        list_line_added[0] += len(set(line_type_annotation_added))
        list_line_removed[0] += len(set(line_type_annotation_removed))

    if len(code_changes_new) > 0:
        # statistics.commits_with_typeChanges += 1
        # tot_this_repo_commit_with_annotations[0] += 1
        # commit_with_annotations_this_repo[0] += 1
        at_least_one_type_change[0] += 1

        code_changes += code_changes_new

    # lock.release()


def TypeAnnotationExtractionLast(repo_path, repo_name, commit, patch, url, statistics,  # lock, logging,
                                 at_least_one_type_change, code_changes,
                                 typeannotation_line_inserted, typeannotation_line_removed, typeannotation_line_changed,
                                 list_line_added, list_line_removed, commit_year):
    code_changes_new = []

    line_type_annotation_added = []
    line_type_annotation_removed = []
    line_type_annotation_changed = []

    old_out = subprocess.Popen(
        ["git", "--git-dir", str(repo_path + repo_name) + '/.git', 'show',
         str(commit.hex + '^') + ":" + str(patch.delta.old_file.path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    old_stdout, old_stderr = old_out.communicate()

    new_out = subprocess.Popen(["git", "--git-dir", str(repo_path + repo_name) + '/.git', 'show',
                                str(commit.hex) + ":" + str(patch.delta.new_file.path)],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    new_stdout, new_stderr = new_out.communicate()

    try:
        node_list_old, node_list_new = extract_from_snippet_new_new(
            str(old_stdout.decode('utf-8-sig')),
            str(new_stdout.decode('utf-8-sig')))
    except Exception as e:
        print(str(e))
        return

    try:

        #########################################################################
        #### RETURN AND ARGUMEN TYPE Annotations                  ###############
        #########################################################################

        for hunk in patch.hunks:
            for annotation_old in node_list_old:
                if annotation_old.line not in range(hunk.old_start, hunk.old_start + hunk.old_lines):
                    continue
                j = -1
                flag_insert = True
                for annotation_new in node_list_new:
                    j += 1
                    if annotation_new.line not in range(hunk.new_start, hunk.new_start + hunk.new_lines):
                        continue

                    if annotation_old.type == annotation_new.type and annotation_old.variable == annotation_new.variable:
                        if annotation_old.annotation == annotation_new.annotation:
                            del node_list_new[j]
                            flag_insert = False
                            break
                        else:
                            #print('[CHANGED]', annotation_old.type, annotation_old.annotation, ' -> ',annotation_new.annotation)

                            temp = CodeChange(url + str(annotation_old.line), commit_year, annotation_old.type, '[CHANGED]',
                                              str(patch.delta.old_file.path),
                                              annotation_old.annotation,
                                              str(annotation_old.line),
                                              str(patch.delta.new_file.path),
                                              annotation_new.annotation,
                                              str(annotation_new.line))

                            code_changes_new.append(temp)

                            statistics.number_type_annotations_per_repo[repo_name] += 1
                            statistics.total_typeAnnotation_codeChanges += 1
                            statistics.modify_existing_types += 1

                            line_type_annotation_changed.append(str(annotation_old.line))

                            if (annotation_old.annotation + ' -> ' + annotation_new.annotation).lower() not in statistics.typeChanged_dict:
                                statistics.typeChanged_dict[
                                    str(annotation_old.annotation + ' -> ' + annotation_new.annotation).lower()] = 1
                            else:
                                statistics.typeChanged_dict[str(str(
                                    annotation_old.annotation + ' -> ' + annotation_new.annotation).lower()).lower()] += 1
                            statistics.total_changed += 1

                            if annotation_old.type == 'return':
                                statistics.functionReturnsType_changed += 1
                            elif annotation_old.type == 'argument':
                                statistics.functionArgsType_changed += 1
                            elif annotation_old.type == 'variable':
                                statistics.variableType_changed += 1

                            del node_list_new[j]
                            flag_insert = False
                            break

                if flag_insert:
                    #print('[REMOVED]', annotation_old.type, annotation_old.annotation)

                    temp = CodeChange(url + str(annotation_old.line), commit_year,annotation_old.type, '[REMOVED]',
                                      str(patch.delta.old_file.path),
                                      annotation_old.annotation,
                                      str(annotation_old.line),
                                      ' ',
                                      ' ',
                                      ' ')

                    code_changes_new.append(temp)

                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    statistics.remove_types += 1

                    line_type_annotation_removed.append(str(annotation_old.line))

                    if annotation_old.annotation.lower() not in statistics.typeRemoved_dict:
                        statistics.typeRemoved_dict[annotation_old.annotation.lower()] = 1
                    else:
                        statistics.typeRemoved_dict[annotation_old.annotation.lower()] += 1

                    statistics.total_removed += 1

                    if annotation_old.type == 'return':
                        statistics.functionReturnsType_removed += 1
                    elif annotation_old.type == 'argument':
                        statistics.functionArgsType_removed += 1
                    elif annotation_old.type == 'variable':
                        statistics.variableType_removed += 1

                    flag_insert = True

            for remained in node_list_new:
                if remained.line in range(hunk.new_start, hunk.new_start + hunk.new_lines):
                    #print('[INSERTED]', remained.type, remained.annotation)
                    temp = CodeChange(url+ str(remained.line), commit_year, remained.type, '[INSERTED]',
                                      ' ',
                                      ' ',
                                      ' ',
                                      str(patch.delta.new_file.path),
                                      remained.annotation,
                                      str(remained.line))

                    code_changes_new.append(temp)

                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    statistics.insert_types += 1
                    # type_annotation_added_this_commit += 1
                    line_type_annotation_added.append(str(remained.line))

                    if remained.annotation.lower() not in statistics.typeAdded_dict:
                        statistics.typeAdded_dict[remained.annotation.lower()] = 1
                    else:
                        statistics.typeAdded_dict[remained.annotation.lower()] += 1

                    statistics.total_added += 1

                    if remained.type == 'return':
                        statistics.functionReturnsType_added += 1
                    elif remained.type == 'argument':
                        statistics.functionArgsType_added += 1
                    elif remained.type == 'variable':
                        statistics.variableType_added += 1

        #print('ok', commit.hex, '\n\n')

    except Exception as e:
        print('[Error changeExtraction]', repo_path, commit, str(e))

    if len(line_type_annotation_added) > 0:
        # statistics.list_typeAnnotation_added_per_commit.append(type_annotation_added_this_commit)
        typeannotation_line_inserted[0] += len(set(line_type_annotation_added))
        list_line_added[0] += len(set(line_type_annotation_added))

    if len(line_type_annotation_removed) > 0:
        # statistics.list_typeAnnotation_removed_per_commit.append(type_annotation_removed_this_commit)
        typeannotation_line_removed[0] += len(set(line_type_annotation_removed))
        list_line_removed[0] += len(set(line_type_annotation_removed))

    if len(line_type_annotation_changed) > 0:
        # statistics.list_typeAnnotation_changed_per_commit.append(type_annotation_changed_this_commit)
        typeannotation_line_inserted[0] += len(set(line_type_annotation_changed))
        typeannotation_line_removed[0] += len(set(line_type_annotation_changed))
        typeannotation_line_changed[0] += len(set(line_type_annotation_changed))

        list_line_added[0] += len(set(line_type_annotation_added))
        list_line_removed[0] += len(set(line_type_annotation_removed))

    if len(code_changes_new) > 0:
        # statistics.commits_with_typeChanges += 1
        # tot_this_repo_commit_with_annotations[0] += 1
        # commit_with_annotations_this_repo[0] += 1
        at_least_one_type_change[0] += 1

        code_changes += code_changes_new



def TypeAnnotationExtractionLastold(repo_path, repo_name, commit, patch, url, statistics,  # lock, logging,
                                    at_least_one_type_change, code_changes,
                                    typeannotation_line_inserted, typeannotation_line_removed,
                                    typeannotation_line_changed,
                                    list_line_added, list_line_removed, commit_year):
    code_changes_new = []

    line_type_annotation_added = []
    line_type_annotation_removed = []
    line_type_annotation_changed = []

    old_out = subprocess.Popen(
        ["git", "--git-dir", str(repo_path + repo_name) + '/.git', 'show',
         str(commit.hex + '^') + ":" + str(patch.delta.old_file.path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    old_stdout, old_stderr = old_out.communicate()

    new_out = subprocess.Popen(["git", "--git-dir", str(repo_path + repo_name) + '/.git', 'show',
                                str(commit.hex) + ":" + str(patch.delta.new_file.path)],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    new_stdout, new_stderr = new_out.communicate()

    if "fatal" in str(new_stdout):
        node_list_new = []
        node_var_list_new = []
    elif "fatal" in str(old_stdout):
        node_list_old = []
        node_var_list_old = []
    else:
        try:
            node_list_old, node_list_new, node_var_list_old, node_var_list_new = extract_from_snippet_new(
                str(old_stdout.decode('utf-8-sig')),
                str(new_stdout.decode('utf-8-sig')))
        except:
            return

    try:

        #########################################################################
        #### RETURN AND ARGUMEN TYPE Annotations                  ###############
        #########################################################################
        flag_arg_insertion = True

        for element_old in node_list_old:
            if len(node_list_new) == 0:
                for element_old in node_list_old:
                    if hasattr(element_old, 'params'):
                        if hasattr(element_old.params, 'params'):
                            for parameter_old in element_old.params.params:
                                if hasattr(parameter_old.annotation, 'annotation'):
                                    if hasattr(parameter_old.annotation.annotation, 'value'):
                                        print('[ARG][REMOVED] ', parameter_old.annotation.annotation.value)
                if hasattr(element_old, 'returns'):
                    if hasattr(element_old.returns, 'annotation'):
                        if hasattr(element_old.returns, 'annotation'):
                            if hasattr(element_old.returns.annotation, 'value'):
                                print('[RETURN][REMOVED] ', element_old.returns.annotation.value)

            for element_new in node_list_new:
                if element_old.name.value == element_new.name.value:
                    if hasattr(element_old, 'params') or hasattr(element_old, 'returns') \
                            and hasattr(element_new, 'params') or hasattr(element_new, 'returns'):
                        if hasattr(element_old.params, 'params') and hasattr(element_new.params, 'params'):
                            list_param_old = list(element_old.params.params)
                            list_param_new = list(element_new.params.params)
                            for parameter_old in list_param_old:
                                i = -1
                                for parameter_new in list_param_new:
                                    i += 1
                                    if parameter_old.name.value == parameter_new.name.value:
                                        if hasattr(parameter_old, 'annotation') and hasattr(parameter_new,
                                                                                            'annotation'):
                                            if hasattr(parameter_old.annotation, 'annotation') and hasattr(
                                                    parameter_new.annotation, 'annotation'):
                                                if hasattr(parameter_old.annotation.annotation, 'value') and hasattr(
                                                        parameter_new.annotation.annotation, 'value'):
                                                    if hasattr(parameter_old.annotation.annotation.value,
                                                               'value') and hasattr(
                                                        parameter_new.annotation.annotation.value, 'value'):
                                                        if parameter_old.annotation.annotation.value.value != parameter_new.annotation.annotation.value.value:
                                                            print('[ARG][CHANGE1] ',
                                                                  parameter_old.annotation.annotation.value.value,
                                                                  ' -> ',
                                                                  parameter_new.annotation.annotation.value.value)
                                                        else:
                                                            del list_param_new[i]

                                                        flag_arg_insertion = False
                                                        break

                                                    else:
                                                        if parameter_old.annotation.annotation.value != parameter_new.annotation.annotation.value:
                                                            print('[ARG][CHANGE2] ',
                                                                  parameter_old.annotation.annotation.value, ' -> ',
                                                                  parameter_new.annotation.annotation.value)
                                                        else:
                                                            del list_param_new[i]

                                                        flag_arg_insertion = False
                                                        break
                                if flag_arg_insertion:
                                    if hasattr(parameter_old.annotation, 'annotation'):
                                        if hasattr(parameter_old.annotation.annotation, 'value'):
                                            print('[ARG][REMOVED] ', parameter_old.annotation.annotation.value)
                                flag_arg_insertion = True
                        # if flag_arg_insertion:
                        #    for parameter_old in element_old.params.params:
                        #        if hasattr(parameter_old.annotation, 'annotation'):
                        #            print('[ARG][INSERTED] ', parameter_old.annotation.annotation.value)
                        flag_arg_insertion = True

                        if hasattr(element_old, 'returns') and hasattr(element_new, 'returns'):
                            if hasattr(element_old.returns, 'annotation') and hasattr(element_new.returns,
                                                                                      'annotation'):
                                if hasattr(element_old.returns.annotation, 'value') and hasattr(
                                        element_new.returns.annotation, 'value'):
                                    if element_old.returns.annotation.value != element_new.returns.annotation.value:
                                        print('[RETURN][CHANGE] ', element_old.returns.annotation.value, ' -> ',
                                              element_new.returns.annotation.value)
                            else:
                                if type(element_old.returns == 'NoneType') and hasattr(element_new.returns,
                                                                                       'annotation'):
                                    if hasattr(element_new.returns.annotation, 'value'):
                                        print('[RETURN][INSERTED] ', element_new.returns.annotation.value)
                                elif type(element_new.returns == 'NoneType') and hasattr(element_old.returns,
                                                                                         'annotation'):
                                    if hasattr(element_old.returns.annotation, 'value'):
                                        print('[RETURN][REMOVED] ', element_old.returns.annotation.value)

        flag_arg_insertion = True

        for element_new in node_list_new:
            if len(node_list_old) == 0:
                for element_new in node_list_new:
                    if hasattr(element_new, 'params'):
                        if hasattr(element_new.params, 'params'):
                            for parameter_new in element_new.params.params:
                                if hasattr(parameter_new.annotation, 'annotation'):
                                    if hasattr(parameter_new.annotation.annotation, 'value'):
                                        print('[ARG][INSERTED] ', parameter_new.annotation.annotation.value)

                if hasattr(element_new, 'returns'):
                    if hasattr(element_new.returns, 'annotation'):
                        if hasattr(element_new.returns, 'annotation'):
                            if hasattr(element_new.returns.annotation, 'value'):
                                print('[RETURN][INSERTED] ', element_new.returns.annotation.value)

            for element_old in node_list_old:
                if element_old.name.value == element_new.name.value:
                    if hasattr(element_old, 'params') or hasattr(element_old, 'returns') \
                            and hasattr(element_new, 'params') or hasattr(element_new, 'returns'):
                        if hasattr(element_old.params, 'params') and hasattr(element_new.params, 'params'):
                            list_param_old = list(element_old.params.params)
                            list_param_new = list(element_new.params.params)
                            for parameter_new in list_param_new:
                                i = -1
                                for parameter_old in list_param_old:
                                    i += 1
                                    if parameter_old.name.value == parameter_new.name.value:
                                        if hasattr(parameter_old, 'annotation') and hasattr(parameter_new,
                                                                                            'annotation'):
                                            if hasattr(parameter_old.annotation, 'annotation') and hasattr(
                                                    parameter_new.annotation, 'annotation'):
                                                if hasattr(parameter_old.annotation.annotation, 'value') and hasattr(
                                                        parameter_new.annotation.annotation, 'value'):
                                                    if hasattr(parameter_old.annotation.annotation.value,
                                                               'value') and hasattr(
                                                        parameter_new.annotation.annotation.value, 'value'):
                                                        if parameter_old.annotation.annotation.value.value != parameter_new.annotation.annotation.value.value:
                                                            pass
                                                        else:
                                                            del list_param_old[i]

                                                        flag_arg_insertion = False
                                                        break

                                                    else:
                                                        if parameter_old.annotation.annotation.value != parameter_new.annotation.annotation.value:
                                                            pass
                                                        else:
                                                            del list_param_old[i]

                                                        flag_arg_insertion = False
                                                        break
                                if flag_arg_insertion:
                                    if hasattr(parameter_new.annotation, 'annotation'):
                                        print('[ARG][INSERTED] ', parameter_new.annotation.annotation.value)
                                flag_arg_insertion = True

        #########################################################################
        ####              VARIABLE TYPE Annotations               ###############
        #########################################################################

        flag_var = True

        for var_old_element in node_var_list_old:
            for var_new_element in node_var_list_new:

                if hasattr(var_old_element, 'body') and hasattr(var_new_element, 'body'):
                    list_var_old = list(var_old_element.body)
                    list_var_new = list(var_new_element.body)
                    for variable_old in list_var_old:
                        for variable_new in list_var_new:
                            if variable_old.target.value == variable_new.target.value:
                                if hasattr(variable_old, 'annotation') and hasattr(variable_new, 'annotation'):
                                    if hasattr(variable_old.annotation, 'annotation') and hasattr(
                                            variable_new.annotation, 'annotation'):
                                        if hasattr(variable_old.annotation.annotation, 'value') and hasattr(
                                                variable_new.annotation.annotation, 'value'):
                                            if hasattr(variable_old.annotation.annotation.value, 'value') and hasattr(
                                                    variable_new.annotation.annotation.value, 'value'):
                                                print('[VAR][CHANGE] ', variable_old.annotation.annotation.value.value,
                                                      ' -> ', variable_new.annotation.annotation.value.value)
                                            else:
                                                print('[VAR][CHANGE2] ', variable_old.annotation.annotation.value,
                                                      ' -> ', variable_new.annotation.annotation.value)

                                            flag_var = False
                                            break

                        if flag_var:
                            if hasattr(variable_old.annotation, 'annotation'):
                                if hasattr(variable_old.annotation.annotation, 'value'):
                                    if hasattr(variable_old.annotation.annotation.value, 'value'):
                                        print('[VAR][REMOVED] ', variable_old.annotation.annotation.value.value)
                        flag_var = True

        print('ok', commit.hex, '\n\n')




    except Exception as e:
        print('Error changeExtraction:', repo_path, commit, str(e))
        # print('Repository', repo_path, 'commit', commit, 'with old line', str(old_stdout))

    # lock.acquire()
    if len(line_type_annotation_added) > 0:
        # statistics.list_typeAnnotation_added_per_commit.append(type_annotation_added_this_commit)
        typeannotation_line_inserted[0] += len(set(line_type_annotation_added))
        list_line_added[0] += len(set(line_type_annotation_added))

    if len(line_type_annotation_removed) > 0:
        # statistics.list_typeAnnotation_removed_per_commit.append(type_annotation_removed_this_commit)
        typeannotation_line_removed[0] += len(set(line_type_annotation_removed))
        list_line_removed[0] += len(set(line_type_annotation_removed))

    if len(line_type_annotation_changed) > 0:
        # statistics.list_typeAnnotation_changed_per_commit.append(type_annotation_changed_this_commit)
        typeannotation_line_inserted[0] += len(set(line_type_annotation_changed))
        typeannotation_line_removed[0] += len(set(line_type_annotation_changed))
        typeannotation_line_changed[0] += len(set(line_type_annotation_changed))

        list_line_added[0] += len(set(line_type_annotation_added))
        list_line_removed[0] += len(set(line_type_annotation_removed))

    if len(code_changes_new) > 0:
        # statistics.commits_with_typeChanges += 1
        # tot_this_repo_commit_with_annotations[0] += 1
        # commit_with_annotations_this_repo[0] += 1
        at_least_one_type_change[0] += 1

        code_changes += code_changes_new

    # lock.release()


def TypeAnnotationExtractionFirstCommit(repo_path, repo_name, commit, patch, url, statistics,  # lock, logging,
                                        at_least_one_type_change, code_changes,
                                        typeannotation_line_inserted, typeannotation_line_removed,
                                        typeannotation_line_changed, list_line_added, commit_year):
    # command = "git --git-dir " + str(repo_path) + '/.git show ' + str(commit.hex) + ":" + str(patch.delta.old_file.path)
    # os.system(command)
    code_changes_new = []
    type_annotation_added_this_commit = 0
    type_annotation_removed_this_commit = 0
    type_annotation_changed_this_commit = 0

    line_type_annotation_added = []

    new_out = subprocess.Popen(["git", "--git-dir", str(repo_path + repo_name) + '/.git', 'show',
                                str(commit.hex) + ":" + str(patch.delta.new_file.path)],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    new_stdout, new_stderr = new_out.communicate()

    if "fatal" in str(new_stdout):
        return

    try:
        new_param_types, new_return_types, new_variable_types = extract_from_snippet(str(new_stdout.decode('utf-8')))
    except:
        return

    try:
        old_line = old_code = new_line = new_code = ' '
        ################################################################
        ########  RETURN TYPE ANNOTATIONS                          #####
        ################################################################

        # Insert type annotation
        for key in new_return_types:
            try:
                new_line, new_code = search_key_value_in_snippet(str(new_stdout.decode('utf-8')),
                                                                 [key, new_return_types[key]])
            except:
                old_line = old_code = new_line = new_code = ' '

            temp = CodeChange(url + str(new_line), commit_year, str(patch.delta.old_file.path), '', '',
                              str(patch.delta.new_file.path),
                              new_line, str(new_return_types[key]))

            # if temp not in code_changes_new:
            code_changes_new.append(temp)

            # lock.acquire()
            statistics.number_type_annotations_per_repo[repo_name] += 1
            statistics.total_typeAnnotation_codeChanges += 1
            statistics.insert_types += 1
            # type_annotation_added_this_commit += 1
            line_type_annotation_added.append(new_line)

            if new_return_types[key].lower() not in statistics.typeAdded_dict:
                statistics.typeAdded_dict[new_return_types[key].lower()] = 1
            else:
                statistics.typeAdded_dict[new_return_types[key].lower()] += 1
            statistics.total_added += 1
            statistics.functionReturnsType_added += 1
            # list_line_added.add(key)
            # lock.release()

        ################################################################
        ########  ARGUMENTS TYPE ANNOTATIONS                       #####
        ################################################################

        # Insert type annotation
        for key in new_param_types:
            try:
                new_line, new_code = search_key_value_in_snippet(str(new_stdout.decode('utf-8')),
                                                                 [key, new_param_types[key]])
            except:
                old_line = old_code = new_line = new_code = ' '

            temp = CodeChange(url + str(new_line), commit_year, str(patch.delta.old_file.path), '', '',
                              str(patch.delta.new_file.path),
                              new_line, str(new_param_types[key]))

            # if temp not in code_changes_new:
            code_changes_new.append(temp)

            # lock.acquire()
            statistics.number_type_annotations_per_repo[repo_name] += 1
            statistics.total_typeAnnotation_codeChanges += 1
            statistics.insert_types += 1
            # type_annotation_added_this_commit += 1
            line_type_annotation_added.append(new_line)

            if new_param_types[key].lower() not in statistics.typeAdded_dict:
                statistics.typeAdded_dict[new_param_types[key].lower()] = 1
            else:
                statistics.typeAdded_dict[new_param_types[key].lower()] += 1
            statistics.total_added += 1
            statistics.functionArgsType_added += 1
            # list_line_added.add(key)
            # lock.release()

            ################################################################
            ########  VARIABLE TYPE ANNOTATIONS                        #####
            ################################################################

            # Insert type annotation
            for key in new_variable_types:
                try:
                    new_line, new_code = search_key_value_in_snippet(str(new_stdout.decode('utf-8')),
                                                                     [key, new_variable_types[key]])
                except:
                    old_line = old_code = new_line = new_code = ' '

                temp = CodeChange(url + str(new_line), commit_year, str(patch.delta.old_file.path), '', '',
                                  str(patch.delta.new_file.path),
                                  new_line, str(new_variable_types[key]))

                # if temp not in code_changes_new:
                code_changes_new.append(temp)

                # lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.insert_types += 1
                # type_annotation_added_this_commit += 1
                line_type_annotation_added.append(new_line)

                if new_variable_types[key].lower() not in statistics.typeAdded_dict:
                    statistics.typeAdded_dict[new_variable_types[key].lower()] = 1
                else:
                    statistics.typeAdded_dict[new_variable_types[key].lower()] += 1
                statistics.total_added += 1
                statistics.variableType_added += 1
                # list_line_added.add(key)
                # lock.release()
    except:
        # print('Repository', repo_path, 'commit', commit, 'with old line', str(old_stdout))
        pass

    # lock.acquire()
    if len(line_type_annotation_added) > 0:
        # statistics.list_typeAnnotation_added_per_commit.append(type_annotation_added_this_commit)
        typeannotation_line_inserted[0] += len(set(line_type_annotation_added))
        list_line_added[0] += len(set(line_type_annotation_added))

    if len(code_changes_new) > 0:
        # statistics.commits_with_typeChanges += 1
        # tot_this_repo_commit_with_annotations[0] += 1
        # commit_with_annotations_this_repo[0] += 1
        at_least_one_type_change[0] += 1

        code_changes += code_changes_new

    # lock.release()


# [RQ7]: How many of all types are annotated in the last version of the code?
def type_annotation_in_last_version(repo_name, statistics):  # , lock):
    for filepath in pathlib.Path(config.ROOT_DIR + "/GitHub/" + repo_name).glob('**/*'):
        temp = []
        if str(filepath).endswith(".py"):
            try:
                param_types, return_types, variable_types = extract_from_file(str(filepath))

                if (not param_types) and (not return_types) and (not variable_types):
                    continue

                for key in param_types:
                    # if str(key) not in temp:
                    temp.append(str(key))

                for key in return_types:
                    # if str(key) not in temp:
                    temp.append(str(key))

                for key in variable_types:
                    # if str(key) not in temp:
                    temp.append(str(key))

                # lock.acquire()
                if repo_name not in statistics.typeLastProjectVersion_dict:
                    statistics.typeLastProjectVersion_dict[repo_name] = len(temp)
                else:
                    statistics.typeLastProjectVersion_dict[repo_name] += len(temp)
                statistics.typeLastProjectVersion_total += len(temp)

                #  statistics.typeLastProjectVersion_dict[repo_name] += len(param_types)
                #  statistics.typeLastProjectVersion_total += len(param_types)

                # lock.release()

            except:
                pass
