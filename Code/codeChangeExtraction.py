import os
import pathlib
import subprocess
import config
from Code.codeChange import CodeChange
from Code.parsers import TypeCollector
import libcst as cst


def extract_from_snippet(string):
    if len(string) == 0:
        return {}, {}, {}

    # Parse file to AST
    #try:
        # str_file = string[2:-1].replace("\\n", os.linesep).replace("\\t", "    ").replace("= \\'", "= '").replace("\\\\", "\\")
        # ast = cst.parse_module(string[2:-1].replace("\\n", os.linesep).replace("\\t", "    "))
    ast = cst.parse_module(string)
   # except Exception as e:
        # print('Failed to upload to ftp: ' + str(e))
       # return {}, {}, {}

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

def search_key_value_in_snippet(file, list_of_strings):
    #Get line from the file along with line numbers, which contains any string from the list
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



def TypeAnnotationExtraction(repo_path, repo_name, commit, patch, url, statistics,# lock, logging,
                             at_least_one_type_change, code_changes,
                             typeannotation_line_inserted, typeannotation_line_removed, typeannotation_line_changed,
                             list_line_added, list_line_removed, commit_year):
    # command = "git --git-dir " + str(repo_path) + '/.git show ' + str(commit.hex) + ":" + str(patch.delta.old_file.path)
    # os.system(command)
    code_changes_new = []
    type_annotation_added_this_commit = 0
    type_annotation_removed_this_commit = 0
    type_annotation_changed_this_commit = 0

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
            new_param_types, new_return_types, new_variable_types = extract_from_snippet(str(new_stdout.decode('utf-8')))
        except:
            return

    try:
        old_line = old_code = new_line = new_code = ' '

        """
        escape = 0
        for key in old_param_types:
            if escape == len(old_param_types):
                break

            if len(key) == 3:
                key2 = tuple( key[:1] + tuple([old_param_types[key]]) + key[2:])

                old_param_types[key2] = old_param_types[key]
                del old_param_types[key]

            escape += 1

        escape = 0
        for key in old_return_types:
            if escape == len(old_return_types):
                break

            if len(key) == 3:
                key2 = tuple( key[:1] + tuple([old_return_types[key]])  + key[2:])

                old_return_types[key2] = old_return_types[key]
                del old_return_types[key]

            escape += 1

        escape = 0
        for key in old_variable_types:
            if escape == len(old_variable_types):
                break

            if len(key) == 3:
                key2 = tuple( key[:1] + tuple([old_variable_types[key]]) + key[2:])

                old_variable_types[key2] = old_variable_types[key]
                del old_variable_types[key]

            escape += 1

        escape = 0
        for key in new_param_types:
            if escape == len(new_param_types):
                break

            if len(key) == 3:
                key2 = tuple(key[:1] + tuple([new_param_types[key]]) + key[2:])

                new_param_types[key2] = new_param_types[key]
                del new_param_types[key]

            escape += 1

        escape = 0
        for key in new_return_types:
            if escape == len(new_return_types):
                break

            if len(key) == 3:
                key2 = tuple(key[:1] + tuple([new_return_types[key]]) + key[2:])

                new_return_types[key2] = new_return_types[key]
                del new_return_types[key]

            escape += 1

        escape = 0
        for key in new_variable_types:
            if escape == len(new_variable_types):
                break

            if len(key) == 3:
                key2 = tuple(key[:1] + tuple([new_variable_types[key]]) + key[2:])

                new_variable_types[key2] = new_variable_types[key]
                del new_variable_types[key]

            escape += 1
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

                    temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line, str(old_return_types[key]),
                                      str(patch.delta.new_file.path),
                                      new_line, str(new_return_types[key]))

                    # if temp not in code_changes_new:
                    code_changes_new.append(temp)

                    #lock.acquire()
                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    statistics.modify_existing_types += 1
                    #type_annotation_changed_this_commit += 1
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
                    #list_line_added.add(key)
                    #list_line_removed.add(key)

                    #lock.release()

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

                temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line, str(old_return_types[key]),
                                  str(patch.delta.new_file.path),
                                  '', '')

                # if temp not in code_changes_new:
                code_changes_new.append(temp)

                #lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.remove_types += 1
                #type_annotation_removed_this_commit += 1
                line_type_annotation_removed.append(old_line)

                if old_return_types[key].lower() not in statistics.typeRemoved_dict:
                    statistics.typeRemoved_dict[old_return_types[key].lower()] = 1
                else:
                    statistics.typeRemoved_dict[old_return_types[key].lower()] += 1
                statistics.total_removed += 1
                statistics.functionReturnsType_removed += 1
                #list_line_removed.add(key)
                #lock.release()

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

                #lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.insert_types += 1
                #type_annotation_added_this_commit += 1
                line_type_annotation_added.append(new_line)

                if new_return_types[key].lower() not in statistics.typeAdded_dict:
                    statistics.typeAdded_dict[new_return_types[key].lower()] = 1
                else:
                    statistics.typeAdded_dict[new_return_types[key].lower()] += 1
                statistics.total_added += 1
                statistics.functionReturnsType_added += 1

                #list_line_added.add(key)
                #lock.release()

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

                    temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line, str(old_param_types[key]),
                                      str(patch.delta.new_file.path),
                                      new_line, str(new_param_types[key]))

                    # if temp not in code_changes_new:
                    code_changes_new.append(temp)

                    #lock.acquire()
                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    statistics.modify_existing_types += 1
                    #type_annotation_changed_this_commit += 1
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

                    #list_line_added.add(key)
                    #list_line_removed.add(key)

                    #lock.release()

            # Remove type annotation
            else:
                try:
                    old_line, old_code = search_key_value_in_snippet(str(old_stdout.decode('utf-8')),
                                                                     [key, old_param_types[key]])
                except:
                    old_line = old_code = new_line = new_code = ' '

                temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line, str(old_param_types[key]),
                                  str(patch.delta.new_file.path),
                                  '', '')

                # if temp not in code_changes_new:
                code_changes_new.append(temp)

                #lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.remove_types += 1
                #type_annotation_removed_this_commit += 1
                line_type_annotation_removed.append(old_line)

                if old_param_types[key].lower() not in statistics.typeRemoved_dict:
                    statistics.typeRemoved_dict[old_param_types[key].lower()] = 1
                else:
                    statistics.typeRemoved_dict[old_param_types[key].lower()] += 1
                statistics.total_removed += 1
                statistics.functionArgsType_removed += 1

                #list_line_removed.add(key)
                #lock.release()

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

                #lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.insert_types += 1
                #type_annotation_added_this_commit += 1
                line_type_annotation_added.append(new_line)

                if new_param_types[key].lower() not in statistics.typeAdded_dict:
                    statistics.typeAdded_dict[new_param_types[key].lower()] = 1
                else:
                    statistics.typeAdded_dict[new_param_types[key].lower()] += 1
                statistics.total_added += 1
                statistics.functionArgsType_added += 1

                #list_line_added.add(key)
                #lock.release()

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

                    temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line, str(old_variable_types[key]),
                                      str(patch.delta.new_file.path),
                                      new_line, str(new_variable_types[key]))

                    # if temp not in code_changes_new:
                    code_changes_new.append(temp)

                    #lock.acquire()
                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    statistics.modify_existing_types += 1
                    #type_annotation_changed_this_commit += 1
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

                    #list_line_added.add(key)
                    #list_line_removed.add(key)

                    #lock.release()

            # Remove type annotation
            else:
                try:
                    old_line, old_code = search_key_value_in_snippet(
                        str(new_stdout.decode('utf-8')),
                        [key, old_variable_types[key]])
                except:
                    old_line = old_code = new_line = new_code = ' '

                if key in old_variable_types:
                    temp = CodeChange(url + str(old_line), commit_year, str(patch.delta.old_file.path), old_line, str(old_variable_types[key]),
                                      str(patch.delta.new_file.path),
                                      '', '')

                    # if temp not in code_changes_new:
                    code_changes_new.append(temp)

                    #lock.acquire()
                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    statistics.remove_types += 1
                    #type_annotation_removed_this_commit += 1
                    line_type_annotation_removed.append(old_line)

                    if old_variable_types[key].lower() not in statistics.typeRemoved_dict:
                        statistics.typeRemoved_dict[old_variable_types[key].lower()] = 1
                    else:
                        statistics.typeRemoved_dict[old_variable_types[key].lower()] += 1
                    statistics.total_removed += 1
                    statistics.variableType_removed += 1

                    #list_line_removed.add(key)
                    #lock.release()

        # Insert type annotation
        for key in new_variable_types:
            if key not in old_variable_types:
                try:
                    new_line, new_code = search_key_value_in_snippet(
                        str(new_stdout.decode('utf-8')),
                        [key, new_variable_types[key]])
                except:
                    old_line = old_code = new_line = new_code = ' '

                temp = CodeChange(url + str(new_line),commit_year, str(patch.delta.old_file.path), '', '',
                                  str(patch.delta.new_file.path),
                                  new_line, str(new_variable_types[key]))

                # if temp not in code_changes_new:
                code_changes_new.append(temp)

                #lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.insert_types += 1
                #type_annotation_added_this_commit += 1
                line_type_annotation_added.append(new_line)

                if new_variable_types[key].lower() not in statistics.typeAdded_dict:
                    statistics.typeAdded_dict[new_variable_types[key].lower()] = 1
                else:
                    statistics.typeAdded_dict[new_variable_types[key].lower()] += 1
                statistics.total_added += 1
                statistics.variableType_added += 1

                #list_line_added.add(key)
                #lock.release()
    except Exception as e:
        print('Error changeExtraction:', repo_path, commit, str(e))
        # print('Repository', repo_path, 'commit', commit, 'with old line', str(old_stdout))

    #lock.acquire()
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

    #lock.release()


def TypeAnnotationExtractionFirstCommit(repo_path, repo_name, commit, patch, url, statistics,# lock, logging,
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

            #lock.acquire()
            statistics.number_type_annotations_per_repo[repo_name] += 1
            statistics.total_typeAnnotation_codeChanges += 1
            statistics.insert_types += 1
            #type_annotation_added_this_commit += 1
            line_type_annotation_added.append(new_line)

            if new_return_types[key].lower() not in statistics.typeAdded_dict:
                statistics.typeAdded_dict[new_return_types[key].lower()] = 1
            else:
                statistics.typeAdded_dict[new_return_types[key].lower()] += 1
            statistics.total_added += 1
            statistics.functionReturnsType_added += 1
            #list_line_added.add(key)
            #lock.release()

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

            #lock.acquire()
            statistics.number_type_annotations_per_repo[repo_name] += 1
            statistics.total_typeAnnotation_codeChanges += 1
            statistics.insert_types += 1
            #type_annotation_added_this_commit += 1
            line_type_annotation_added.append(new_line)

            if new_param_types[key].lower() not in statistics.typeAdded_dict:
                statistics.typeAdded_dict[new_param_types[key].lower()] = 1
            else:
                statistics.typeAdded_dict[new_param_types[key].lower()] += 1
            statistics.total_added += 1
            statistics.functionArgsType_added += 1
            #list_line_added.add(key)
            #lock.release()

            ################################################################
            ########  VARIABLE TYPE ANNOTATIONS                        #####
            ################################################################

            # Insert type annotation
            for key in new_variable_types:
                try:
                    new_line, new_code = search_key_value_in_snippet(str(new_stdout.decode('utf-8')),[key, new_variable_types[key]])
                except:
                    old_line = old_code = new_line = new_code = ' '

                temp = CodeChange(url + str(new_line), commit_year, str(patch.delta.old_file.path), '', '',
                                  str(patch.delta.new_file.path),
                                  new_line, str(new_variable_types[key]))

                # if temp not in code_changes_new:
                code_changes_new.append(temp)

                #lock.acquire()
                statistics.number_type_annotations_per_repo[repo_name] += 1
                statistics.total_typeAnnotation_codeChanges += 1
                statistics.insert_types += 1
                #type_annotation_added_this_commit += 1
                line_type_annotation_added.append(new_line)

                if new_variable_types[key].lower() not in statistics.typeAdded_dict:
                    statistics.typeAdded_dict[new_variable_types[key].lower()] = 1
                else:
                    statistics.typeAdded_dict[new_variable_types[key].lower()] += 1
                statistics.total_added += 1
                statistics.variableType_added += 1
                #list_line_added.add(key)
                #lock.release()
    except:
        # print('Repository', repo_path, 'commit', commit, 'with old line', str(old_stdout))
        pass

    #lock.acquire()
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

    #lock.release()


# [RQ7]: How many of all types are annotated in the last version of the code?
def type_annotation_in_last_version(repo_name, statistics):#, lock):
    for filepath in pathlib.Path(config.ROOT_DIR + "/GitHub/" + repo_name).glob('**/*'):
        temp = []
        if str(filepath).endswith(".py"):
            try:
                param_types, return_types, variable_types = extract_from_file(str(filepath))

                if (not param_types) and (not return_types) and (not variable_types):
                    continue

                for key in param_types:
                    #if str(key) not in temp:
                    temp.append(str(key))

                for key in return_types:
                    #if str(key) not in temp:
                    temp.append(str(key))

                for key in variable_types:
                   # if str(key) not in temp:
                    temp.append(str(key))

                #lock.acquire()
                if repo_name not in statistics.typeLastProjectVersion_dict:
                    statistics.typeLastProjectVersion_dict[repo_name] = len(temp)
                else:
                    statistics.typeLastProjectVersion_dict[repo_name] += len(temp)
                statistics.typeLastProjectVersion_total += len(temp)

                #  statistics.typeLastProjectVersion_dict[repo_name] += len(param_types)
                #  statistics.typeLastProjectVersion_total += len(param_types)

                #lock.release()

            except:
                pass
