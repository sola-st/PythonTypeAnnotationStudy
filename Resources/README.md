TODO: new column?: Relationship of between the newly fixed type and the type suggested by pyre. (e.g. Sequence -> List = subtype)

TODO: fix download code script for pyre-fixme 
# type_fix_dataset #
Contains json data where each entry is a code change to fix a type error.

Currently, there are 125 fixes recorded.

## Fields ##
`"isolated_code_change"`: Minimal code change required to perform the fix in git-diff format. Note that 1 change could fix multiple errors, in this case, each error will produce an entry.

`"type_error"`: Types of error that was fixed by this code change. From pyre warning.

`"code_transform"`: Category of the type of code change, which is one of the followings:
- MODIFY_FUN_RETURN_VALUE
- MODIFY_FUN_RETURN_TYPE
- MODIFY_FUN_PARAM_TYPE
- MODIFY_FUN_PARAM_VAL
- REMOVE
- REMOVE_TYPE
- MODIFY_VAR_TYPE
- OP_CHANGE
- CASTING
- ADD_RETURN_VAL
- RENAME_VAR
- CHANGE_EXPRESSION
- MODIFY_METHOD_CALL
- MODIFY_ISINSTANCE_CALL
- ADD_NONE_CHECK
- MODIFY_ATTR_TYPE
- REMOVE_REANNOTATION
- MODIFY_RETURN_TYPE

`"involved_types"`: Indicates all type involved in this fix, including before and after fix. Including types that only appeared in pyre warning messages. Composite types are broken down, e.g. `Union[int, str]` -> `"involved_types":["Union", "str", "int"]`.
- `Text` = alias for `str`

`"type_change"`: Category of the type annotation change, which is one of the followings:
- ADDED
- REPLACED
- REMOVED
- NONE

`"location"`: Location of the code change relative to the pyre warning message, which is one of the followings:
- ENCLOSING_FUN_RETURN
- ENCLOSING_FUN_PARAM
- ENCLOSING_FUN
- EXACT_LINE
- FUN_CALLEE
- CLASS_ATTR
- SUPERCLASS_ATTR
- ENCLOSING_IF

`"full_warning_msg"`: Warning message produced by pyre prior to the fix (i.e. the parent commit). `pyre-fixme` (i.e. a suppressed pyre warning) is also included when it's type error gets fixed.

`"url"`: Url to the commit where this type fix happens. 

`"change_runtime"`: Boolean, `true` if the fix changes python runtime behavior.

`"mentioned_by_pyre"`: Boolean, `true` if the fixed (i.e. new) type annotation is mentioned in the pyre warning message. Some special cases:
- `true` if a subclass of the mentioned types is used
- `true` if `Optional[T]`/`None` is used when `None` is mentioned
- `true` if `Callable[T]` is used when the error type is Call error
- `true` if the new type can be represented by the mentioned types, e.g. true if `List[tuple[]]` is used when `List[Any]` is mentioned

`"pyre_detail"`: Explains how developers use the hint given by pyre. 
- Potential value if `"mentioned_by_pyre"` is `true`:
  - `"EXACT_MENTIONED_TYPE"`
  - More specific kind of `"EXACT_MENTIONED_TYPE"`:
    - `"USE_EXPECTED_TYPE"` (e.g. "Expected A but got B" -> A = `EXPECTED_TYPE`)
    - `"USE_NOT_EXPECTED_TYPE"` (e.g. "v is declared to have type "A" but is used as type "B" -> B = `NOT_EXPECTED_TYPE`)
    - `"USE_OPTIONAL_FOR_NONE"` (a more specific kind of `"EXACT_MENTIONED_TYPE"`)
    - `"USE_OVERRIDEN_TYPE"` (only for `Inconsistent override [15]`)
  - `"PARTIAL_MENTIONED_TYPE"` (e.g. pyre mentions `Component`, dev uses `Optional[Component]`)
  - `"USE_SUPER_TYPE"`
  - `"USE_SUBCLASS"` (e.g. Animal -> Dog)
  - `"USE_SUBTYPE"` (= narrower than suggested types)
  - `"REDUNDANT_HINT"` (only for `Redundant Cast [22]`)
  - `"CANNOT_REANNOTATE"` (only for `Illegal annotation target [35]`)
  - `"ASSIGN_VALUE_OF_TYPE"`
  - `"USE_CALLABLE"` (only for `Call error [29]`)
- Potential value if `"mentioned_by_pyre"` is `false`: (Usually no hints are given if it is `Invalid type [31]` or `Undefined attribute [16]`)
  - `"CALL_CORRECT_METHOD"`
  - `"USE_ANOTHER_TYPE"`
  - `"USE_ANY"`
  - `"CAST_STR_ENCODING"`
  - `"REMOVE"`
  <!-- - `"NO_SUGGESTION"` -->

<!-- `"custom_type"`: Boolean, `true` if a customly defined type is used, e.g. `license_formats: ElementsType = ()` with `ElementsType = Union[Sequence[T], Dict[T, float], KeysView[T]]`. -->

`"filepath"`: Optional. Show the filepath where the code change happens. Non-existent if file is the same as the one shown in the earning

# type_fix_code_data #
Contains old and new code from different type fixes. It is structured as `{repo}/{commit}/{old_code}` and `{repo}/{commit}/{new_code}`. Intermediate folders are kept. Downloaded by running `script_download_codes.py`.

# Output_type_fix_commits #
Contains commits that have less pyre type warnings than their parent commits. Used for selecting interesting commits to analyze.

It displays the warnings in both parent and child commits. Only warnings from *files that have a less number of warnings than parents* are shown. Generated from `script_AnalyzeRepos.py`.