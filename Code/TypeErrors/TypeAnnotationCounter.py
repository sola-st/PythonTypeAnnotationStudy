#!/usr/bin/python3

# Tested with Python 3.7.5

import typing
from Code.parsers import TypeCollector
import libcst as cst
import pathlib
import os
from typing import Set

# Extract type annations from a python file


def compute_vars_without_types(scopes, names_with_type: Set[cst.Name]):
    result = []
    for scope in scopes:
        names_without_type: Set[str] = set()
        for assignment in scope.assignments:
            if isinstance(assignment, cst.metadata.Assignment) and isinstance(assignment.node, cst.Name):
                name = assignment.node
                if name not in names_with_type:
                    names_without_type.add(name.value)
        result.extend(list(names_without_type))

    return result


def extract_from_file(file_path: str):
    with open(file_path, 'r') as file:
        src = file.read()

    # Parse file to AST
    try:
        ast = cst.parse_module(src)
    except:
        return {}, {}, {}, {}, {}, {}

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


def count_type_annotations(project_path: str):
    number_param_types: int = 0
    number_return_types: int = 0
    number_variable_types: int = 0
    number_non_param_types: int = 0
    number_non_return_types: int = 0
    number_non_variable_types: int = 0

    counted = 0
    for filepath in pathlib.Path(project_path).glob('**/*'):
        if str(filepath).endswith(".py"):
            counted += 1
            try:
                param_types, return_types, variable_types, non_param_types, non_return_types, non_variable_types = extract_from_file(
                    str(filepath))
                number_param_types += len(param_types)
                number_return_types += len(return_types)
                number_variable_types += len(variable_types)
                number_non_param_types += len(non_param_types)
                number_non_return_types += len(non_return_types)
                number_non_variable_types += len(non_variable_types)
            except Exception as e:
                #print(str(e))
                continue

        counted += 1
           # if counted % 100 == 0:
            #    print(f"Counted annotations in {counted} files")

    return number_param_types, number_return_types, number_variable_types, number_non_param_types, number_non_return_types, number_non_variable_types


if __name__ == "__main__":
    param_types, return_types, variable_types, non_param_types, non_return_types, non_variable_types = count_type_annotations(
        "data/repos/django")
    print(param_types, return_types, variable_types)
