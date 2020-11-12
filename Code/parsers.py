from typing import Dict, List, Optional, Union, TYPE_CHECKING, Tuple, Set

import libcst as cst
from libcst.metadata import PositionProvider


class TypeCollector(cst.CSTVisitor):
    '''
    Collects types from function signatures
    '''

    def __init__(self):

        # stack for storing the canonical name of the current function
        self.wrapper = None
        self.stack: List[Tuple[str, ...]] = []

        self.return_types: Dict[Tuple[str, ...], str] = {}
        self.param_annotations: Dict[Tuple[str, ...], str] = {}
        self.variable_annotations: Dict[Tuple[str, ...], str] = {}
        self.non_return_types: Dict[Tuple[str, ...], str] = {}
        self.non_param_annotations: Dict[Tuple[str, ...], str] = {}
        self.names_with_type: Set[cst.Name] = set()

        # Parse state for descenting into annotations
        self.in_annotation: bool = False
        self.in_attribute: bool = False
        self.in_variable_annotation: bool = False
        self.annotation_parts: List[str] = []
        self.last_annotation: Optional[str] = None

    def visit_Annotation(self, node):

        # if not self.in_variable_annotation:
        self.in_annotation = True
        self.annotation_parts = []
        self.last_annotation = None
        # print(cst.tool.dump(node))

    def visit_Param(self, node):
        self.annotation_parts = []
        self.last_annotation = None

    def visit_AnnAssign(self, node):
        try:
            # if 'Name' not in node.target.value:
            self.stack.append(node.target.value.value)
        except:
            try:
                self.stack.append(node.target.value)
            except:
                return

    def leave_AnnAssign(self, node):
        try:
            if len(self.annotation_parts) > 0:
                # self.variable_annotations[(*self.stack, node.value.value)] = self.last_annotation
                self.variable_annotations[(*self.stack,)] = \
                    self.last_annotation

                if isinstance(node.target, cst.Name):
                    self.names_with_type.add(node.target)
            self.stack.pop()
        except:
            return

    def visit_Name(self, node):
        if self.in_annotation:
            if not self.in_attribute:
                self.annotation_parts.append(node.value)

    def leave_Slice(self, node):
        if self.in_annotation:
            self.annotation_parts.append(",")

    def leave_Element(self, node):
        if self.in_annotation:
            self.annotation_parts.append(",")

    def visit_SubscriptElement(self, node):
        if self.in_annotation:
            self.annotation_parts.append("[")

    def leave_SubscriptElement(self, node):
        if self.in_annotation:
            self.annotation_parts.append("]")

    def visit_List(self, node):
        if self.in_annotation:
            self.annotation_parts.append("[")

    def visit_Attribute(self, node):
        if self.in_annotation:
            self.in_attribute = True

    def leave_Attribute(self, node):
        self.in_attribute = False
        if self.in_annotation:
            type_annotation = ""
            for child in node.children:
                if isinstance(child, cst.Name):
                    type_annotation += child.value
                else:
                    type_annotation += "."
            self.annotation_parts.append(type_annotation)

    def leave_List(self, node):
        if self.in_annotation:
            self.annotation_parts.append("]")

    def leave_Ellipsis(self, node):
        if self.in_annotation:
            self.annotation_parts.append("...")

    def leave_Annotation(self, node):
        if node.annotation.value == 'float':
            i = 0
        # if not self.in_variable_annotation:
        self.in_annotation = False
        self.last_annotation = ''.join(self.annotation_parts). \
            replace('][', ','). \
            replace(',]', ']')

    def visit_ClassDef(self, node: cst.ClassDef):
        self.stack.append(node.name.value)

    def leave_ClassDef(self, node: cst.ClassDef):
        self.stack.pop()

    def visit_FunctionDef(self, node: cst.FunctionDef):
        self.stack.append(node.name.value)

    def leave_FunctionDef(self, node: cst.FunctionDef):
        if len(self.annotation_parts) > 0:
            self.return_types[tuple(self.stack)] = \
                self.last_annotation
        else:
            self.non_return_types[tuple(self.stack)] = None

        self.annotation_parts = []
        self.last_annotation = None
        self.stack.pop()

    def leave_Param(self, node: cst.Param):
        if len(self.annotation_parts) > 0:
            METADATA_DEPENDENCIES = ( PositionProvider,)
            #pos = METADATA_DEPENDENCIES.get_metadata(PositionProvider, node).start
          #  result = ParamPrinter().visit_Name(self, node)
          #result = node.visit(ParamPrinter())

            self.param_annotations[(*self.stack, node.name.value)] = \
                self.last_annotation
        else:
            self.non_param_annotations[(*self.stack, node.name.value)] = None

        self.annotation_parts = []
        self.last_annotation = None


class IsParamProvider(cst.BatchableMetadataProvider[bool]):
    """
    Marks Name nodes found as a parameter to a function.
    """

    def __init__(self) -> None:
        super().__init__()
        self.is_param = False

    def visit_Param(self, node: cst.Param) -> None:
        # Mark the child Name node as a parameter
        self.set_metadata(node.name, True)

    def visit_Name(self, node: cst.Name) -> None:
        # Mark all other Name nodes as not parameters
        if not self.get_metadata(type(self), node, False):
            self.set_metadata(node, False)


class ParamPrinter(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (IsParamProvider, PositionProvider,)

    def visit_Name(self, node: cst.Name) -> None:
        # Only print out names that are parameters
        if self.get_metadata(IsParamProvider, node):
            pos = self.get_metadata(PositionProvider, node).start
            print(f"{node.value} found at line {pos.line}, column {pos.column}")
            #return pos.line
