import re
import pathlib
import subprocess
from datetime import datetime

import config
from Code.TypeAnnotations.codeChange import CodeChange, SingleDiffChange
from Code.TypeErrors.TypeAnnotationCounter import compute_vars_without_types
from Code.parsers import TypeCollector
import libcst as cst
import copy
import sys
from libcst.metadata import PositionProvider


def extract_from_snippet(string):
    try:
        if len(string) == 0:
            return {}, {}, {}, {}, {}, {}

        # Parse file to AST
        # try:
        # str_file = string[2:-1].replace("\\n", os.linesep).replace("\\t", "    ").replace("= \\'", "= '").replace("\\\\", "\\")
        # ast = cst.parse_module(string[2:-1].replace("\\n", os.linesep).replace("\\t", "    "))

        ast = cst.parse_module(string)

        # Pre-compute scopes
        wrapper = cst.metadata.MetadataWrapper(ast)
        scopes = set(wrapper.resolve(cst.metadata.ScopeProvider).values())

        # Collect types
        type_collector = TypeCollector()
        wrapper.visit(type_collector)

        param_types = type_collector.param_annotations
        return_types = type_collector.return_types
        variable_types = type_collector.variable_annotations

        non_param_types = type_collector.non_param_annotations
        non_return_types = type_collector.non_return_types
        non_variable_types = compute_vars_without_types(scopes, type_collector.names_with_type)

        return param_types, return_types, variable_types, non_param_types, non_return_types, non_variable_types
    except:
        return {}, {}, {}, {}, {}, {}


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

    brackets = ""

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
                                            if parameter.annotation.annotation.value.value.lower() in ['list', 'tuple',
                                                                                                       'range']:
                                                brackets = "["
                                                for child_type in parameter.annotation.annotation.children:
                                                    if 'SubscriptElement' in type(child_type).__name__:
                                                        for child_annotation in child_type.children:
                                                            if 'Comma' in type(child_annotation).__name__:
                                                                brackets += ","
                                                                continue

                                                            if hasattr(child_annotation, 'value'):
                                                                if hasattr(child_annotation.value, 'value'):
                                                                    if 'Name' in type(
                                                                            child_annotation.value.value).__name__:
                                                                        brackets += child_annotation.value.value.value
                                                                    else:
                                                                        brackets += child_annotation.value.value
                                                                else:
                                                                    brackets += "..."

                                                brackets += ']'

                                            # print('[ARG] ', parameter.annotation.annotation.value.value, '->', pos)
                                            annotation_node = SingleDiffChange('argument', 'old', parameter.name.value,
                                                                               parameter.annotation.annotation.value.value + brackets,
                                                                               pos.start.line, pos.start.column)
                                            node_list_old.append(annotation_node)
                                            brackets = ""
                                        else:
                                            # print('[ARG2] ', parameter.annotation.annotation.value, '->', pos)
                                            if hasattr(parameter.annotation.annotation, 'value'):
                                                annotation_node = SingleDiffChange('argument', 'old',
                                                                                   parameter.name.value,
                                                                                   parameter.annotation.annotation.value,
                                                                                   pos.start.line, pos.start.column)
                                                node_list_old.append(annotation_node)

                    if hasattr(node, 'returns'):
                        if hasattr(node.returns, 'annotation'):
                            if hasattr(node.returns.annotation, 'value'):
                                if hasattr(node.returns.annotation.value, 'value'):
                                    if node.returns.annotation.value.value.lower() in ['list', 'tuple',
                                                                                       'range']:
                                        brackets = "["
                                        for child_type in node.returns.annotation.children:
                                            if 'SubscriptElement' in type(child_type).__name__:
                                                for child_annotation in child_type.children:
                                                    if 'Comma' in type(child_annotation).__name__:
                                                        brackets += ","
                                                        continue

                                                    if hasattr(child_annotation, 'value'):
                                                        if hasattr(child_annotation.value, 'value'):
                                                            if 'Name' in type(child_annotation.value.value).__name__:
                                                                brackets += child_annotation.value.value.value
                                                            else:
                                                                brackets += child_annotation.value.value
                                                        else:
                                                            brackets += "..."

                                        brackets += ']'

                                # print('[RETURN] ', node.returns.annotation.value, '->', pos)
                                if hasattr(node.returns.annotation.value, 'value') and 'Name' in type(
                                        node.returns.annotation.value).__name__:
                                    annotation_node = SingleDiffChange('return', 'new', node.name.value,
                                                                       node.returns.annotation.value.value + brackets,
                                                                       pos.start.line, pos.start.column)
                                else:
                                    annotation_node = SingleDiffChange('return', 'new', node.name.value,
                                                                       node.returns.annotation.value + brackets,
                                                                       pos.start.line, pos.start.column)

                                node_list_old.append(annotation_node)
                                brackets = ""
            else:
                if 'SimpleStatementLine' in type(node).__name__:
                    if hasattr(node, 'body'):
                        for variable in node.body:
                            if hasattr(variable, 'annotation'):
                                if hasattr(variable.annotation, 'annotation'):
                                    if hasattr(variable.annotation.annotation, 'value'):
                                        if hasattr(variable.annotation.annotation.value, 'value'):
                                            if variable.annotation.annotation.value.value.lower() in ['list', 'tuple',
                                                                                                      'range']:
                                                brackets = "["
                                                for child_type in variable.annotation.annotation.children:
                                                    if 'SubscriptElement' in type(child_type).__name__:
                                                        for child_annotation in child_type.children:
                                                            if 'Comma' in type(child_annotation).__name__:
                                                                brackets += ","
                                                                continue

                                                            if hasattr(child_annotation, 'value'):
                                                                if hasattr(child_annotation.value, 'value'):
                                                                    if 'Name' in type(
                                                                            child_annotation.value.value).__name__:
                                                                        brackets += child_annotation.value.value.value
                                                                    else:
                                                                        brackets += child_annotation.value.value
                                                                else:
                                                                    brackets += "..."

                                                brackets += ']'
                                            # print('[VAR] ', variable.annotation.annotation.value.value, '->', pos)
                                            annotation_node = SingleDiffChange('variable', 'old', variable.target.value,
                                                                               variable.annotation.annotation.value.value + brackets,
                                                                               pos.start.line, pos.start.column)
                                            node_list_old.append(annotation_node)
                                        else:
                                            # print('[VAR2] ', variable.annotation.annotation.value, '->', pos)
                                            if hasattr(variable.annotation.annotation, 'value'):
                                                annotation_node = SingleDiffChange('variable', 'old',
                                                                                   variable.target.value,
                                                                                   variable.annotation.annotation.value,
                                                                                   pos.start.line, pos.start.column)
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
                                            if parameter.annotation.annotation.value.value.lower() in ['list', 'tuple',
                                                                                                       'range']:
                                                brackets = "["
                                                for child_type in parameter.annotation.annotation.children:
                                                    if 'SubscriptElement' in type(child_type).__name__:
                                                        for child_annotation in child_type.children:
                                                            if 'Comma' in type(child_annotation).__name__:
                                                                brackets += ","
                                                                continue

                                                            if hasattr(child_annotation, 'value'):
                                                                if hasattr(child_annotation.value, 'value'):
                                                                    if 'Name' in type(
                                                                            child_annotation.value.value).__name__:
                                                                        brackets += child_annotation.value.value.value
                                                                    else:
                                                                        brackets += child_annotation.value.value
                                                                else:
                                                                    brackets += "..."

                                                brackets += ']'

                                            # print('[ARG] ', parameter.annotation.annotation.value.value, '->', pos)
                                            annotation_node = SingleDiffChange('argument', 'new', parameter.name.value,
                                                                               parameter.annotation.annotation.value.value + brackets,
                                                                               pos.start.line, pos.start.column)
                                            node_list_new.append(annotation_node)
                                            brackets = ""
                                        else:
                                            # print('[ARG2] ', parameter.annotation.annotation.value, '->', pos)
                                            annotation_node = SingleDiffChange('argument', 'new', parameter.name.value,
                                                                               parameter.annotation.annotation.value,
                                                                               pos.start.line, pos.start.column)
                                            node_list_new.append(annotation_node)
                    if hasattr(node, 'returns'):
                        if hasattr(node.returns, 'annotation'):
                            if hasattr(node.returns.annotation, 'value'):
                                if hasattr(node.returns.annotation.value, 'value'):

                                    temp_type_check = node.returns.annotation.value.value
                                    while True:
                                        if 'str' in type(temp_type_check).__name__:
                                            break

                                        temp_type_check = temp_type_check.value

                                    if node.returns.annotation.value.value.lower() in ['list', 'tuple',
                                                                                       'range']:
                                        brackets = "["
                                        for child_type in node.returns.annotation.children:
                                            if 'SubscriptElement' in type(child_type).__name__:
                                                for child_annotation in child_type.children:
                                                    if 'Comma' in type(child_annotation).__name__:
                                                        brackets += ","
                                                        continue

                                                    if hasattr(child_annotation, 'value'):
                                                        if hasattr(child_annotation.value, 'value'):
                                                            if 'Name' in type(child_annotation.value.value).__name__:
                                                                brackets += child_annotation.value.value.value
                                                            else:
                                                                brackets += child_annotation.value.value
                                                        else:
                                                            brackets += "..."

                                        brackets += ']'

                                # print('[RETURN] ', node.returns.annotation.value, '->', pos)
                                if hasattr(node.returns.annotation.value, 'value') and 'Name' in type(
                                        node.returns.annotation.value).__name__:
                                    annotation_node = SingleDiffChange('return', 'new', node.name.value,
                                                                       node.returns.annotation.value.value + brackets,
                                                                       pos.start.line, pos.start.column)
                                else:
                                    annotation_node = SingleDiffChange('return', 'new', node.name.value,
                                                                       node.returns.annotation.value + brackets,
                                                                       pos.start.line, pos.start.column)
                                node_list_new.append(annotation_node)
                                brackets = ""
            else:
                if 'SimpleStatementLine' in type(node).__name__:
                    if hasattr(node, 'body'):
                        for variable in node.body:
                            if hasattr(variable, 'annotation'):
                                if hasattr(variable.annotation, 'annotation'):
                                    if hasattr(variable.annotation.annotation, 'value'):
                                        if hasattr(variable.annotation.annotation.value, 'value'):
                                            if variable.annotation.annotation.value.value.lower() in ['list', 'tuple',
                                                                                                      'range']:
                                                brackets = "["
                                                for child_type in variable.annotation.annotation.children:
                                                    if 'SubscriptElement' in type(child_type).__name__:
                                                        for child_annotation in child_type.children:
                                                            if 'Comma' in type(child_annotation).__name__:
                                                                brackets += ","
                                                                continue

                                                            if hasattr(child_annotation, 'value'):
                                                                if hasattr(child_annotation.value, 'value'):
                                                                    if 'Name' in type(
                                                                            child_annotation.value.value).__name__:
                                                                        brackets += child_annotation.value.value.value
                                                                    else:
                                                                        brackets += child_annotation.value.value
                                                                else:
                                                                    brackets += "..."

                                                brackets += ']'
                                            # print('[VAR] ', variable.annotation.annotation.value.value, '->', pos)
                                            annotation_node = SingleDiffChange('variable', 'new', variable.target.value,
                                                                               variable.annotation.annotation.value.value + brackets,
                                                                               pos.start.line, pos.start.column)
                                            node_list_new.append(annotation_node)
                                        else:
                                            # print('[VAR2] ', variable.annotation.annotation.value, '->', pos)
                                            annotation_node = SingleDiffChange('variable', 'new', variable.target.value,
                                                                               variable.annotation.annotation.value,
                                                                               pos.start.line, pos.start.column)
                                            node_list_new.append(annotation_node)

    return node_list_old, node_list_new


def extract_from_snippet_new_new_new(string_old, string_new, file_old, file_new):
    # if len(string_old) == 0:
    #   return {}, {}, {}

    # string_old = "from typing import Any\n" + "def process_something(arguments: Any, func:int, f2:str, fooo)-> int:\n " \
    #                                          "  pass\nx:List[int] = []\ny:List[int] = []\nx = 0 "

    # string_new = "from typing import Any\n" + "def process_something(arguments: Any, func, f2:float, fooo: " \
    #                                         "complex):\n   pass\nx = []\ny:Tuple[int] = []\nx:float = 0 "

    node_list_new = []
    node_list_old = []

    brackets = ""

    if not ("fatal: Path" in str(string_old) and "does not exist in" in str(string_old)):
        ast_old = cst.parse_module(string_old)
        wrapper_old = cst.metadata.MetadataWrapper(ast_old)
        positions_old = wrapper_old.resolve(PositionProvider)

        # For the old file
        for node, pos in positions_old.items():
            if 'Param' in type(node).__name__:
                if hasattr(node, 'annotation'):
                    if hasattr(node.annotation, 'annotation'):
                        if hasattr(node.annotation.annotation, 'value'):
                            if hasattr(node.annotation.annotation.value, 'value'):
                                if node.annotation.annotation.value.value.lower() in ['list', 'tuple',
                                                                                      'range']:
                                    brackets = collection_type_annotation_recursive(
                                        node.annotation.annotation.slice).replace("][", ",")

                                # print('[ARG] ', parameter.annotation.annotation.value.value, '->', pos)
                                annotation_node = SingleDiffChange('argument', 'new',  file_old, node.name.value,
                                                                   node.annotation.annotation.value.value + brackets,
                                                                   pos.start.line, pos.start.column)
                                node_list_old.append(annotation_node)
                                brackets = ""
                            else:
                                # print('[ARG2] ', parameter.annotation.annotation.value, '->', pos)
                                annotation_node = SingleDiffChange('argument', 'new',  file_old,node.name.value,
                                                                   node.annotation.annotation.value,
                                                                   pos.start.line, pos.start.column)
                                node_list_old.append(annotation_node)


            # Return annotation, es. def foo() -> str:
            elif 'FunctionDef' in type(node).__name__:
                if hasattr(node, 'returns'):
                    if hasattr(node.returns, 'annotation'):
                        if hasattr(node.returns.annotation, 'value'):
                            if hasattr(node.returns.annotation.value, 'value'):
                                if node.returns.annotation.value.value.lower() in ['list', 'tuple',
                                                                                   'range']:
                                    brackets = collection_type_annotation_recursive(
                                        node.returns.annotation.slice).replace("][", ",")

                            # print('[RETURN] ', node.returns.annotation.value, '->', pos)
                            if hasattr(node.returns.annotation.value, 'value') and 'Name' in type(
                                    node.returns.annotation.value).__name__:
                                annotation_node = SingleDiffChange('return', 'new', file_old, node.name.value,
                                                                   node.returns.annotation.value.value + brackets,
                                                                   pos.start.line, pos.start.column)
                            else:
                                annotation_node = SingleDiffChange('return', 'new', file_old, node.name.value,
                                                                   node.returns.annotation.value + brackets,
                                                                   pos.start.line, pos.start.column)

                            node_list_old.append(annotation_node)
                            brackets = ""

            # Variable Annotation, es. x:int = 5
            else:
                if 'SimpleStatementLine' in type(node).__name__:
                    if hasattr(node, 'body'):
                        for variable in node.body:
                            if hasattr(variable, 'annotation'):
                                if hasattr(variable.annotation, 'annotation'):
                                    if hasattr(variable.annotation.annotation, 'value'):
                                        if hasattr(variable.annotation.annotation.value, 'value'):
                                            if variable.annotation.annotation.value.value.lower() in ['list', 'tuple',
                                                                                                      'range']:
                                                brackets = collection_type_annotation_recursive(
                                                    variable.annotation.annotation.slice).replace("][", ",")

                                            # print('[VAR] ', variable.annotation.annotation.value.value, '->', pos)
                                            annotation_node = SingleDiffChange('variable', 'new', file_old, variable.target.value,
                                                                               variable.annotation.annotation.value.value + brackets,
                                                                               pos.start.line, pos.start.column)
                                            node_list_old.append(annotation_node)
                                            brackets = ""
                                        else:
                                            # print('[VAR2] ', variable.annotation.annotation.value, '->', pos)
                                            annotation_node = SingleDiffChange('variable', 'new', file_old, variable.target.value,
                                                                               variable.annotation.annotation.value,
                                                                               pos.start.line, pos.start.column)
                                            node_list_old.append(annotation_node)

    # For the new file
    if not ("fatal: Path" in str(string_new) and "does not exist in" in str(string_new)):
        ast_new = cst.parse_module(string_new)
        wrapper_new = cst.metadata.MetadataWrapper(ast_new)
        positions_new = wrapper_new.resolve(PositionProvider)

        for node, pos in positions_new.items():
            if 'Param' in type(node).__name__:
                if hasattr(node, 'annotation'):
                    if hasattr(node.annotation, 'annotation'):
                        if hasattr(node.annotation.annotation, 'value'):
                            if hasattr(node.annotation.annotation.value, 'value'):
                                if node.annotation.annotation.value.value.lower() in ['list', 'tuple',
                                                                                      'range']:
                                    brackets = collection_type_annotation_recursive(
                                        node.annotation.annotation.slice).replace("][", ",")

                                # print('[ARG] ', parameter.annotation.annotation.value.value, '->', pos)
                                annotation_node = SingleDiffChange('argument', 'new', file_new, node.name.value,
                                                                   node.annotation.annotation.value.value + brackets,
                                                                   pos.start.line, pos.start.column)
                                node_list_new.append(annotation_node)
                                brackets = ""
                            else:
                                # print('[ARG2] ', parameter.annotation.annotation.value, '->', pos)
                                annotation_node = SingleDiffChange('argument', 'new',file_new, node.name.value,
                                                                   node.annotation.annotation.value,
                                                                   pos.start.line, pos.start.column)
                                node_list_new.append(annotation_node)

            # Return annotation, es. def foo() -> str:
            elif 'FunctionDef' in type(node).__name__:
                if hasattr(node, 'returns'):
                    if hasattr(node.returns, 'annotation'):
                        if hasattr(node.returns.annotation, 'value'):
                            if hasattr(node.returns.annotation.value, 'value'):
                                if node.returns.annotation.value.value.lower() in ['list', 'tuple',
                                                                                   'range']:
                                    brackets = collection_type_annotation_recursive(
                                        node.returns.annotation.slice).replace("][", ",")

                            # print('[RETURN] ', node.returns.annotation.value, '->', pos)
                            if hasattr(node.returns.annotation.value, 'value') and 'Name' in type(
                                    node.returns.annotation.value).__name__:
                                annotation_node = SingleDiffChange('return', 'new',file_new, node.name.value,
                                                                   node.returns.annotation.value.value + brackets,
                                                                   pos.start.line, pos.start.column)
                            else:
                                annotation_node = SingleDiffChange('return', 'new',file_new, node.name.value,
                                                                   node.returns.annotation.value + brackets,
                                                                   pos.start.line, pos.start.column)

                            node_list_new.append(annotation_node)
                            brackets = ""

            # Variable Annotation, es. x:int = 5
            else:
                if 'SimpleStatementLine' in type(node).__name__:
                    if hasattr(node, 'body'):
                        for variable in node.body:
                            if hasattr(variable, 'annotation'):
                                if hasattr(variable.annotation, 'annotation'):
                                    if hasattr(variable.annotation.annotation, 'value'):
                                        if hasattr(variable.annotation.annotation.value, 'value'):
                                            if variable.annotation.annotation.value.value.lower() in ['list', 'tuple',
                                                                                                      'range']:
                                                brackets = collection_type_annotation_recursive(
                                                    variable.annotation.annotation.slice).replace("][", ",")

                                            # print('[VAR] ', variable.annotation.annotation.value.value, '->', pos)
                                            annotation_node = SingleDiffChange('variable', 'new',file_new, variable.target.value,
                                                                               variable.annotation.annotation.value.value + brackets,
                                                                               pos.start.line, pos.start.column)
                                            node_list_new.append(annotation_node)
                                            brackets = ""
                                        else:
                                            # print('[VAR2] ', variable.annotation.annotation.value, '->', pos)
                                            annotation_node = SingleDiffChange('variable', 'new',file_new, variable.target.value,
                                                                               variable.annotation.annotation.value,
                                                                               pos.start.line, pos.start.column)
                                            node_list_new.append(annotation_node)

    return node_list_old, node_list_new

def handle_param(node, pos, file_old, node_list_old):
    if hasattr(node, 'annotation') and node.annotation is not None:
        if hasattr(node.annotation, 'annotation'):
            if hasattr(node.annotation.annotation, 'value'):
                attribute = ""

                if hasattr(node.annotation.annotation, 'attr'):
                    if hasattr(node.annotation.annotation.attr, 'value'):
                        attribute = "." + str(node.annotation.annotation.attr.value)
                if hasattr(node.annotation.annotation.value, 'value'):
                    if hasattr(node.annotation.annotation, "slice"):
                        brackets = collection_type_annotation_recursive(
                            node.annotation.annotation.slice).replace("][", ",")

                    # print('[ARG] ', parameter.annotation.annotation.value.value, '->', pos)
                    annotation_node = SingleDiffChange('argument', 'old', file_old, node.name.value,
                                                        str(node.annotation.annotation.value.value) + brackets  + attribute,
                                                        pos.start.line, pos.start.column)
                    node_list_old.append(annotation_node)
                    brackets = ""

                else:
                    # print('[ARG2] ', parameter.annotation.annotation.value, '->', pos)
                    annotation_node = SingleDiffChange('argument', 'old',file_old, node.name.value,
                                                        str(node.annotation.annotation.value)  + attribute,
                                                        pos.start.line, pos.start.column)
                    node_list_old.append(annotation_node)               
    # For old file, include nodes without annotation
    else:
        annotation_node = SingleDiffChange('argument', 'old',file_old, node.name.value,
                                            'nil', pos.start.line, pos.start.column)
        node_list_old.append(annotation_node)

def extract_from_snippet_new_new_new_new(string_old, string_new, file_old, file_new):

    node_list_new = []
    node_list_old = []

    # annotation_list_new = []
    # annotation_list_old = []

    brackets = ""

    type_set = set()

    # For the old file
    if not ("fatal: " in str(string_old)):
        ast_old = cst.parse_module(string_old)
        wrapper_old = cst.metadata.MetadataWrapper(ast_old)
        positions_old = wrapper_old.resolve(PositionProvider)

        for node, pos in positions_old.items():
            # print(type(node).__name__)
            type_set.add(type(node).__name__)
                
            if 'Param' == type(node).__name__:
                handle_param(node, pos, file_old, node_list_old)
            elif 'Parameters' == type(node).__name__ and hasattr(node, 'params'):                
                for p in node.params:
                    handle_param(p, pos, file_old, node_list_old)
            # Return annotation, es. def foo() -> str:
            # elif 'Annotation' in type(node).__name__:
            elif 'FunctionDef' in type(node).__name__:
                # print(node)
                if hasattr(node, 'returns') and node.returns is not None:
                    if hasattr(node.returns, 'annotation'):
                        attribute = ""

                        if hasattr(node.returns.annotation, 'attr'):
                            if hasattr(node.returns.annotation.attr, 'value'):
                                attribute = "." + str(node.returns.annotation.attr.value)
                        if hasattr(node.returns.annotation.value, 'value'):
                            if hasattr(node.returns.annotation, "slice"):
                                brackets = collection_type_annotation_recursive(
                                    node.returns.annotation.slice).replace("][", ",")

                        # print('[RETURN] ', node.returns.annotation.value, '->', pos)
                        if hasattr(node.returns.annotation.value, 'value') and 'Name' in type(
                                node.returns.annotation.value).__name__:
                            annotation_node = SingleDiffChange('return', 'old',file_old, node.name.value,
                                                               str(node.returns.annotation.value.value) + brackets  + attribute,
                                                               pos.start.line, pos.start.column)
                        else:
                            annotation_node = SingleDiffChange('return', 'old',file_old, node.name.value,
                                                               str(node.returns.annotation.value) + brackets  + attribute,
                                                               pos.start.line, pos.start.column)

                        node_list_old.append(annotation_node)
                        brackets = ""
                # For old file, include nodes without annotation
                else:
                    annotation_node = SingleDiffChange('return', 'old',file_old, node.name.value,
                                                        'nil', pos.start.line, pos.start.column)
                    node_list_old.append(annotation_node)

            # Variable Annotation, es. x:int = 5
            else:
                if 'SimpleStatementLine' in type(node).__name__:
                    if hasattr(node, 'body'):
                        for variable in node.body:
                            # print(variable)
                            if hasattr(variable, 'annotation'):
                                if hasattr(variable.annotation, 'annotation'):
                                    attribute = ""

                                    if hasattr(variable.annotation.annotation, 'attr'):
                                        if hasattr(variable.annotation.annotation.attr, 'value'):
                                            attribute = "." + str(variable.annotation.annotation.attr.value)

                                    if hasattr(variable.annotation.annotation, 'value'):
                                        if hasattr(variable.annotation.annotation.value, 'value'):
                                            if hasattr(variable.annotation.annotation, "slice"):
                                                brackets = collection_type_annotation_recursive(
                                                    variable.annotation.annotation.slice).replace("][", ",")

                                            # print('[VAR] ', variable.annotation.annotation.value.value, '->', pos)
                                            annotation_node = SingleDiffChange('variable', 'old',file_old, variable.target,
                                                                               str(variable.annotation.annotation.value.value) + brackets  + attribute,
                                                                               pos.start.line, pos.start.column)
                                            node_list_old.append(annotation_node)
                                            brackets = ""

                                        else:
                                            # print('[VAR2] ', variable.annotation.annotation.value, '->', pos)
                                            annotation_node = SingleDiffChange('variable', 'old',file_old, variable.target,
                                                                               str(variable.annotation.annotation.value) + attribute,
                                                                               pos.start.line, pos.start.column)
                                            node_list_old.append(annotation_node)
                            # For old file, include nodes without annotation
                            elif hasattr(variable, 'target'):
                                # print(variable)
                                annotation_node = SingleDiffChange('variable', 'old',file_old, variable.target,
                                                                    'nil', pos.start.line, pos.start.column)
                                node_list_old.append(annotation_node)
                            elif hasattr(variable, 'targets'): # Tuple, Subscript, Name, Attribute, ...
                                for t in variable.targets:
                                    if hasattr(t, 'target'):
                                        annotation_node = SingleDiffChange('variable', 'old',file_old, t.target,
                                                                            'nil', pos.start.line, pos.start.column)
                                        node_list_old.append(annotation_node)

    # For the new file
    if not ("fatal: " in str(string_new)):
        ast_new = cst.parse_module(string_new)
        wrapper_new = cst.metadata.MetadataWrapper(ast_new)
        positions_new = wrapper_new.resolve(PositionProvider)

        for node, pos in positions_new.items():
            # if 'FunctionDef' in type(node).__name__:
            #     print(node)
            if 'Param' in type(node).__name__:
                if hasattr(node, 'annotation'):
                    if hasattr(node.annotation, 'annotation'):
                        if hasattr(node.annotation.annotation, 'value'):
                            attribute = ""

                            if hasattr(node.annotation.annotation, 'attr'):
                                if hasattr(node.annotation.annotation.attr, 'value'):
                                    attribute = "." + str(node.annotation.annotation.attr.value)
                            if hasattr(node.annotation.annotation.value, 'value'):
                                if hasattr(node.annotation.annotation, "slice"):
                                    brackets = collection_type_annotation_recursive(
                                        node.annotation.annotation.slice).replace("][", ",")

                                # print('[ARG] ', parameter.annotation.annotation.value.value, '->', pos)
                                annotation_node = SingleDiffChange('argument', 'new',file_new, node.name.value,
                                                                   str(node.annotation.annotation.value.value) + brackets  + attribute,
                                                                   pos.start.line, pos.start.column)
                                node_list_new.append(annotation_node)
                                brackets = ""
                            else:
                                # print('[ARG2] ', parameter.annotation.annotation.value, '->', pos)
                                annotation_node = SingleDiffChange('argument', 'new',file_new, node.name.value,
                                                                   str(node.annotation.annotation.value)  + attribute,
                                                                   pos.start.line, pos.start.column)
                                node_list_new.append(annotation_node)

            # Return annotation, es. def foo() -> str:
            elif 'FunctionDef' in type(node).__name__:
                if hasattr(node, 'returns') and node.returns is not None:
                    if hasattr(node.returns, 'annotation'):
                        attribute = ""

                        if hasattr(node.returns.annotation, 'attr'):
                            if hasattr(node.returns.annotation.attr, 'value'):
                                attribute = "." + str(node.returns.annotation.attr.value)
                        if hasattr(node.returns.annotation.value, 'value'):
                            if hasattr(node.returns.annotation, "slice"):
                                brackets = collection_type_annotation_recursive(
                                    node.returns.annotation.slice).replace("][", ",")

                        # print('[RETURN] ', node.returns.annotation.value, '->', pos)
                        if hasattr(node.returns.annotation.value, 'value') and 'Name' in type(
                                node.returns.annotation.value).__name__:
                            annotation_node = SingleDiffChange('return', 'new',file_old, node.name.value,
                                                               str(node.returns.annotation.value.value) + brackets  + attribute,
                                                               pos.start.line, pos.start.column)
                        else:
                            annotation_node = SingleDiffChange('return', 'new',file_old, node.name.value,
                                                               str(node.returns.annotation.value) + brackets  + attribute,
                                                               pos.start.line, pos.start.column)

                        node_list_new.append(annotation_node)
                        brackets = ""

            # Variable Annotation, es. x:int = 5
            else:
                if 'SimpleStatementLine' in type(node).__name__:
                    if hasattr(node, 'body'):
                        for variable in node.body:
                            if hasattr(variable, 'annotation'):
                                if hasattr(variable.annotation, 'annotation'):
                                    attribute = ""

                                    if hasattr(variable.annotation.annotation, 'attr'):
                                        if hasattr(variable.annotation.annotation.attr, 'value'):
                                            attribute = "." + str(variable.annotation.annotation.attr.value)

                                    if hasattr(variable.annotation.annotation, 'value'):
                                        if hasattr(variable.annotation.annotation.value, 'value'):
                                            if hasattr(variable.annotation.annotation, "slice"):
                                                brackets = collection_type_annotation_recursive(
                                                    variable.annotation.annotation.slice).replace("][", ",")

                                            # print('[VAR] ', variable.annotation.annotation.value.value, '->', pos)
                                            annotation_node = SingleDiffChange('variable', 'new',file_new, variable.target.value,
                                                                               str(variable.annotation.annotation.value.value) + brackets  + attribute,
                                                                               pos.start.line, pos.start.column)
                                            node_list_new.append(annotation_node)
                                            brackets = ""
                                        else:
                                            # print('[VAR2] ', variable.annotation.annotation.value, '->', pos)
                                            annotation_node = SingleDiffChange('variable', 'new',file_new, variable.target.value,
                                                                               str(variable.annotation.annotation.value) + attribute,
                                                                               pos.start.line, pos.start.column)
                                            node_list_new.append(annotation_node)

    # size_old = len(annotation_list_old)
    # size_new = len(annotation_list_new)

    # for node in node_list_old:
    #     j = -1
    #     for node_return in annotation_list_old:
    #         j += 1
    #         if node.annotation == node_return.annotation and node.line == node_return.line:
    #             del annotation_list_old[j]
    #             break

    # for node in node_list_new:
    #     j = -1
    #     for node_return in annotation_list_new:
    #         j += 1
    #         if node.annotation == node_return.annotation and node.line == node_return.line:
    #             del annotation_list_new[j]
    #             break

    # Debug:
    # print(type_set)
    # print(size_old)
    # print(size_new)
    # print(len(node_list_old))
    # print(len(node_list_new))
    # print(len(annotation_list_old))
    # print(len(annotation_list_new))
    # return node_list_old + annotation_list_old, node_list_new + annotation_list_new
    return node_list_old, node_list_new

    # if size_old == (len(node_list_old) + len(annotation_list_old)) and size_new == (len(node_list_new) + len(annotation_list_new)):
    #     return node_list_old + annotation_list_old, node_list_new + annotation_list_new
    # else:
    #     return extract_from_snippet_new_new_new(string_old, string_new, file_old, file_new)


def collection_type_annotation_recursive(slice) -> str:
    type_ann: str = ""

    if "tuple" in type(slice).__name__:
        for child in slice:
            if hasattr(child, 'value'):
                if hasattr(child.value, 'slice'):
                    type_ann += collection_type_annotation_recursive(child.value.slice)
                elif hasattr(child.value, 'value'):
                    return " " + child.value.value
            else:
                if hasattr(child, 'slice'):
                    type_ann += collection_type_annotation_recursive(child.slice)
                elif hasattr(child, 'value'):
                    if hasattr(child.value, 'slice'):
                        type_ann += collection_type_annotation_recursive(child.value.slice)
                elif hasattr(child.value, 'value'):
                    return " " + child.value.value
    else:
        if hasattr(slice, 'slice'):
            type_ann += collection_type_annotation_recursive(slice.slice)
        elif hasattr(slice, 'value'):
            if hasattr(slice.value, 'slice'):
                type_ann += collection_type_annotation_recursive(slice.value.slice)
            if hasattr(slice.value, 'value'):
                if hasattr(slice.value.value, 'value'):
                    if hasattr(slice.value.value.value, 'value'):
                        if hasattr(slice.value.value.value.value, 'value'):
                            return "[" + str(slice.value.value.value.value.value) + str(type_ann) + "]"
                        else:
                            return "[" + str(slice.value.value.value.value) + str(type_ann) + "]"
                    else:
                        return "[" + str(slice.value.value.value) + str(type_ann) + "]"
                else:
                    return "[" + str(slice.value.value) + str(type_ann) + "]"
            else:
                return "[" + "..." + str(type_ann) + "]"

    return " " + str(type_ann)


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


def TypeAnnotationExtractionLast(repo_path, repo_name, commit, patch, url, statistics,  # lock, logging,
                                 at_least_one_type_change, code_changes,
                                 typeannotation_line_inserted, typeannotation_line_removed, typeannotation_line_changed,
                                 list_line_added, list_line_removed,
                                 commit_year, commit_month, commit_day):
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
        #print(url)
        node_list_old, node_list_new = extract_from_snippet_new_new_new_new(
            str(old_stdout.decode('utf-8-sig')),
            str(new_stdout.decode('utf-8-sig')))
    except Exception as e:
        # print(str(e), repo_path, commit.hex)
        return

    try:
        #########################################################################
        ####                    TYPE Annotations                  ###############
        #########################################################################

        for hunk in patch.hunks:
            # result77 = hashlib.md5("main.py".encode('utf-8')).hexdigest()
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

                        # print('[CHANGED]', annotation_old.type, annotation_old.annotation, ' -> ',annotation_new.annotation)
                        if hasattr(annotation_old.annotation, 'value'):
                            annotation_old.annotation = str(annotation_old.annotation.value)

                        if hasattr(annotation_new.annotation, 'value'):
                            annotation_new.annotation = str(annotation_new.annotation.value)

                        if annotation_old.annotation == annotation_new.annotation:
                            del node_list_new[j]
                            flag_insert = False
                            break

                        temp = CodeChange(url + 'L' + str(annotation_old.line), str(commit_year),
                                          "",
                                          "",
                                          "0",
                                          str(annotation_old.type), '[CHANGED]',
                                          annotation_old.variable,
                                          str(patch.delta.old_file.path),
                                          str(annotation_old.annotation),
                                          str(annotation_old.line),
                                          str(patch.delta.new_file.path),
                                          str(annotation_new.annotation),
                                          str(annotation_new.line))

                        code_changes_new.append(temp)

                        statistics.number_type_annotations_per_repo[repo_name] += 1
                        statistics.total_typeAnnotation_codeChanges += 1

                        if commit_year not in statistics.modify_existing_types:
                            statistics.modify_existing_types[str(commit_year)] = 1
                        else:
                            statistics.modify_existing_types[str(commit_year)] += 1

                        line_type_annotation_changed.append(str(annotation_old.line))

                        if str(annotation_old.type) == 'argument':
                            if (annotation_old.annotation + ' -> ' + annotation_new.annotation).lower() not in statistics.typeChanged_dict_arg:
                                statistics.typeChanged_dict_arg[
                                    str(annotation_old.annotation + ' -> ' + annotation_new.annotation).lower()] = 1
                            else:
                                statistics.typeChanged_dict_arg[str(str(
                                    annotation_old.annotation + ' -> ' + annotation_new.annotation).lower()).lower()] += 1

                        elif str(annotation_old.type) == 'return':
                            if (annotation_old.annotation + ' -> ' + annotation_new.annotation).lower() not in statistics.typeChanged_dict_ret:
                                statistics.typeChanged_dict_ret[
                                    str(annotation_old.annotation + ' -> ' + annotation_new.annotation).lower()] = 1
                            else:
                                statistics.typeChanged_dict_ret[str(str(
                                    annotation_old.annotation + ' -> ' + annotation_new.annotation).lower()).lower()] += 1

                        elif str(annotation_old.type) == 'variable':
                            if (annotation_old.annotation + ' -> ' + annotation_new.annotation).lower() not in statistics.typeChanged_dict_var:
                                statistics.typeChanged_dict_var[
                                    str(annotation_old.annotation + ' -> ' + annotation_new.annotation).lower()] = 1
                            else:
                                statistics.typeChanged_dict_var[str(str(
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
                    # print('[REMOVED]', annotation_old.type, annotation_old.annotation)

                    if hasattr(annotation_old.annotation, 'value'):
                        annotation_old.annotation = str(annotation_old.annotation.value)

                    temp = CodeChange(url + 'L' + str(annotation_old.line), str(commit_year),
                                      "",
                                      f"{commit_year}-{commit_month}-{commit_day}",
                                      "0",
                                      str(annotation_old.type),
                                      '[REMOVED]',
                                      annotation_old.variable,
                                      str(patch.delta.old_file.path),
                                      str(annotation_old.annotation),
                                      str(annotation_old.line),
                                      ' ',
                                      ' ',
                                      ' ')

                    code_changes_new.append(temp)

                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    #statistics.remove_types += 1

                    if commit_year not in statistics.remove_types:
                        statistics.remove_types[commit_year] = 1
                    else:
                        statistics.remove_types[commit_year] += 1

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
                    # print('[INSERTED]', remained.type, remained.annotation)
                    if hasattr(remained.annotation, 'value'):
                        remained.annotation = str(remained.annotation.value)

                    temp = CodeChange(url + 'R' + str(remained.line), str(commit_year),
                                      f"{commit_year}-{commit_month}-{commit_day}",
                                      "",
                                      "0",
                                      str(remained.type),
                                      '[INSERTED]',
                                      remained.variable,
                                      ' ',
                                      ' ',
                                      ' ',
                                      str(patch.delta.new_file.path),
                                      str(remained.annotation),
                                      str(remained.line))

                    code_changes_new.append(temp)

                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    #statistics.insert_types += 1

                    if commit_year not in statistics.insert_types:
                        statistics.insert_types[commit_year] = 1
                    else:
                        statistics.insert_types[commit_year] += 1

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

        # print('ok', commit.hex, '\n\n')

    except Exception as e:
        print('[Error changeExtraction]', repo_path, commit.hex, str(e))

    if len(line_type_annotation_added) > 0:
        typeannotation_line_inserted[0] += len(set(line_type_annotation_added))
        list_line_added[0] += len(set(line_type_annotation_added))

    if len(line_type_annotation_removed) > 0:
        typeannotation_line_removed[0] += len(set(line_type_annotation_removed))
        list_line_removed[0] += len(set(line_type_annotation_removed))

    if len(line_type_annotation_changed) > 0:
        typeannotation_line_inserted[0] += len(set(line_type_annotation_changed))
        typeannotation_line_removed[0] += len(set(line_type_annotation_changed))
        typeannotation_line_changed[0] += len(set(line_type_annotation_changed))

        list_line_added[0] += len(set(line_type_annotation_added))
        list_line_removed[0] += len(set(line_type_annotation_removed))

    if len(code_changes_new) > 0:
        at_least_one_type_change[0] += 1

        code_changes += code_changes_new

def TypeAnnotationExtractionLast_life(repo_path, repo_name, commit, patch, url, statistics,  # lock, logging,
                                 at_least_one_type_change, code_changes, # code_changes stores the metadata of the code change across different commits and patches
                                 typeannotation_line_inserted, typeannotation_line_removed, typeannotation_line_changed,
                                 list_line_added, list_line_removed, commit_year, commit_month, commit_day,
                                 err_dict=None):
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
        #print(url)
        node_list_old, node_list_new = extract_from_snippet_new_new_new_new( # extract PARAM, VAR, RETURN annotation
            str(old_stdout.decode('utf-8-sig')),
            str(new_stdout.decode('utf-8-sig')),
            str(patch.delta.old_file.path),
            str(patch.delta.new_file.path))
    except Exception as e:
        # print(str(e), repo_path, commit.hex)
        return

    try:

        if url == 'https://github.com/ExpDev07/coronavirus-tracker-api/commit/304de58f8db607913feb326e89243082e27c4c50#diff-8426d53622ac8752b5144b1cb827e7e00c1dd33d':
           print("found")
           print("found")


        #########################################################################
        ####                    TYPE Annotations                  ###############
        #########################################################################
        
        # Debug:
        # print('node_list_old', len(node_list_old))
        # for n in node_list_old:
        #     print(n.__dict__)
        # print('node_list_new', len(node_list_new))
        # for n in node_list_new:
        #     print(n.__dict__)        
        

        for hunk in patch.hunks:
            # result77 = hashlib.md5("main.py".encode('utf-8')).hexdigest()
            for annotation_old in node_list_old:
                if annotation_old.line not in range(hunk.old_start, hunk.old_start + hunk.old_lines):
                    continue
                j = -1
                flag_remove = True
                for annotation_new in node_list_new:
                    j += 1
                    if annotation_new.line not in range(hunk.new_start, hunk.new_start + hunk.new_lines):
                        continue
                    # Transformation - Modify: this node/annotation is in both old and new code
                    if annotation_old.type == annotation_new.type and annotation_old.variable == annotation_new.variable and annotation_old.filename == annotation_new.filename:
                        
                        # print('[CHANGED]', annotation_old.type, annotation_old.annotation, ' -> ',annotation_new.annotation)
                        if hasattr(annotation_old.annotation, 'value'):
                            annotation_old.annotation = str(annotation_old.annotation.value)

                        if hasattr(annotation_new.annotation, 'value'):
                            annotation_new.annotation = str(annotation_new.annotation.value)

                        if annotation_old.annotation == annotation_new.annotation:
                            del node_list_new[j]
                            flag_remove = False # annotation is the same, no need to process, quit and remove this
                            break

                        temp = CodeChange("",
                                          "",
                                          url + 'R' + str(annotation_old.line),
                                          str(commit_year),
                                          f"{commit_year}-{commit_month}-{commit_day}",
                                          "",
                                          "-1",
                                          "0",
                                          str(annotation_old.type),
                                          '[CHANGED]',
                                          '' if 'Name' in type(annotation_old.variable).__name__ else annotation_old.variable,
                                          str(patch.delta.old_file.path),
                                          str(annotation_old.annotation),
                                          str(annotation_old.line),
                                          str(patch.delta.new_file.path),
                                          str(annotation_new.annotation),
                                          str(annotation_new.line))  
                        temp.commit_hex = str(commit.hex)
                        temp.old_col = str(annotation_old.col)
                        temp.new_col = str(annotation_new.col)

                        code_changes_new.append(temp)
                        
                        del node_list_new[j]
                        flag_remove = False

                        statistics.number_type_annotations_per_repo[repo_name] += 1
                        statistics.total_typeAnnotation_codeChanges += 1

                        if commit_year not in statistics.modify_existing_types:
                            statistics.modify_existing_types[str(commit_year)] = 1
                        else:
                            statistics.modify_existing_types[str(commit_year)] += 1

                        line_type_annotation_changed.append(str(annotation_old.line))
                        # Counting annotation change:
                        if str(annotation_old.type) == 'argument':
                            if (annotation_old.annotation + ' -> ' + annotation_new.annotation).lower() not in statistics.typeChanged_dict_arg:
                                statistics.typeChanged_dict_arg[
                                    str(annotation_old.annotation + ' -> ' + annotation_new.annotation).lower()] = 1
                            else:
                                statistics.typeChanged_dict_arg[str(str(
                                    annotation_old.annotation + ' -> ' + annotation_new.annotation).lower()).lower()] += 1

                        elif str(annotation_old.type) == 'return':
                            if (annotation_old.annotation + ' -> ' + annotation_new.annotation).lower() not in statistics.typeChanged_dict_ret:
                                statistics.typeChanged_dict_ret[
                                    str(annotation_old.annotation + ' -> ' + annotation_new.annotation).lower()] = 1
                            else:
                                statistics.typeChanged_dict_ret[str(str(
                                    annotation_old.annotation + ' -> ' + annotation_new.annotation).lower()).lower()] += 1

                        elif str(annotation_old.type) == 'variable':
                            if (annotation_old.annotation + ' -> ' + annotation_new.annotation).lower() not in statistics.typeChanged_dict_var:
                                statistics.typeChanged_dict_var[
                                    str(annotation_old.annotation + ' -> ' + annotation_new.annotation).lower()] = 1
                            else:
                                statistics.typeChanged_dict_var[str(str(
                                    annotation_old.annotation + ' -> ' + annotation_new.annotation).lower()).lower()] += 1


                        statistics.total_changed += 1

                        if annotation_old.type == 'return':
                            statistics.functionReturnsType_changed += 1
                        elif annotation_old.type == 'argument':
                            statistics.functionArgsType_changed += 1
                        elif annotation_old.type == 'variable':
                            statistics.variableType_changed += 1

                        # del node_list_new[j]
                        # flag_insert = False
                        break
                # # Transformation - Remove: if annotation_old not found in annotation_new, and there exists an annotation in annotation_old
                if flag_remove and annotation_old.annotation != 'nil':
                    # print('[REMOVED]', annotation_old.type, annotation_old.annotation)

                    if hasattr(annotation_old.annotation, 'value'):
                        annotation_old.annotation = str(annotation_old.annotation.value)

                    temp = CodeChange("",
                                      url + 'R' + str(annotation_old.line),
                                      "",
                                      str(commit_year),
                                      "",
                                      f"{commit_year}-{commit_month}-{commit_day}",
                                      "-1",
                                      "0",
                                      str(annotation_old.type),
                                      '[REMOVED]',
                                      '' if 'Name' in type(annotation_old.variable).__name__ else annotation_old.variable,
                                      str(patch.delta.old_file.path),
                                      annotation_old.annotation,
                                      annotation_old.line,
                                      ' ',
                                      ' ',
                                      ' ')
                    temp.commit_hex = str(commit.hex)
                    temp.old_col = str(annotation_old.col)
                    temp.new_col = ""

                    code_changes_new.append(temp)

                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    #statistics.remove_types += 1

                    if commit_year not in statistics.remove_types:
                        statistics.remove_types[commit_year] = 1
                    else:
                        statistics.remove_types[commit_year] += 1

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

                    flag_remove = True # Don't think we need this
            # Transformation - Insert: remaining annotation in new code (other annotation are processed in the above)
            for remained in node_list_new:
                if remained.line in range(hunk.new_start, hunk.new_start + hunk.new_lines):
                    # print('[INSERTED]', remained.type, remained.annotation)
                    if hasattr(remained.annotation, 'value'):
                        remained.annotation = str(remained.annotation.value)

                    if not isinstance(remained.annotation, str):
                        continue

                    temp = CodeChange(url + 'R' + str(remained.line),
                                      "",
                                      "",
                                      str(commit_year),
                                      f"{commit_year}-{commit_month}-{commit_day}",
                                      "",
                                      "-1",
                                      "0",
                                      str(remained.type),
                                      '[INSERTED]',
                                      '' if 'Name' in type(remained.variable).__name__ else remained.variable,
                                      ' ',
                                      ' ',
                                      ' ',
                                      str(patch.delta.new_file.path),
                                      str(remained.annotation),
                                      str(remained.line))  
                    temp.commit_hex = str(commit.hex)
                    temp.old_col = ' '
                    temp.new_col = str(remained.col)

                    code_changes_new.append(temp)

                    statistics.number_type_annotations_per_repo[repo_name] += 1
                    statistics.total_typeAnnotation_codeChanges += 1
                    #statistics.insert_types += 1

                    if commit_year not in statistics.insert_types:
                        statistics.insert_types[commit_year] = 1
                    else:
                        statistics.insert_types[commit_year] += 1

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

        # print('ok', commit.hex, '\n\n')

    except Exception as e:
        print('[Error changeExtraction]', repo_path, commit.hex, str(e))

    if len(line_type_annotation_added) > 0:
        typeannotation_line_inserted[0] += len(set(line_type_annotation_added))
        list_line_added[0] += len(set(line_type_annotation_added))

    if len(line_type_annotation_removed) > 0:
        typeannotation_line_removed[0] += len(set(line_type_annotation_removed))
        list_line_removed[0] += len(set(line_type_annotation_removed))

    if len(line_type_annotation_changed) > 0:
        typeannotation_line_inserted[0] += len(set(line_type_annotation_changed))
        typeannotation_line_removed[0] += len(set(line_type_annotation_changed))
        typeannotation_line_changed[0] += len(set(line_type_annotation_changed))

        list_line_added[0] += len(set(line_type_annotation_added))
        list_line_removed[0] += len(set(line_type_annotation_removed))
        
    # TODO(wai): Put it here for now for clarity.
    # Should do it in the above before each code_changes_new.append(), here we are looping the list again
    parent_commit = commit.parent_ids[0].hex # Ignoring merge (i.e. len(parent_ids) > 1)
    for c in code_changes_new:
        if parent_commit in err_dict: # TODO: Handle merge
            if c.old_file in err_dict[parent_commit]:
                if c.old_line in err_dict[parent_commit][c.old_file]:
                    # potentially relevant error message (pyre errors that were on the same line)
                    c.relevant_prev_commit_pyre_err = list(err_dict[parent_commit][c.old_file][c.old_line].values())
                    if c.old_col in err_dict[parent_commit][c.old_file][c.old_line]:
                        c.prev_commit_pyre_err = err_dict[parent_commit][c.old_file][c.old_line][c.old_col]

    if len(code_changes_new) > 0:
        at_least_one_type_change[0] += 1

        code_changes += code_changes_new




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

def last_version_analysis(repo_name, statistics):
    for filepath in pathlib.Path(config.ROOT_DIR + "/GitHub/" + repo_name).glob('**/*'):
        temp = []
        if str(filepath).endswith(".py"):
            try:
                pass

            except:
                pass


def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)