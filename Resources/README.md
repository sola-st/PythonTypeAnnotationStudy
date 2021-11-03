# type_fix_dataset #
Contains json data where each entry is a code change to fix a type error.

Currently, there are 74 fixes recorded.

## Fields ##
`"isolated_code_change"`: Minimal code change required to perform the fix in git-diff format. Note that 1 change could fix multiple errors, in this case, each error will produce an entry.

`"type_error"`: Types of error that was fixed by this code change. From pyre warning.

`"code_transform"`: Category of the type of code change, which is one of the followings:
- MODIFY_FUN_RETURN_VALUE
- MODIFY_FUN_RETURN_TYPE
- MODIFY_FUN_PARAM_TYPE
- REMOVE
- REMOVE_TYPE
- MODIFY_VAR_TYPE
- REMOVE_FUN_PARAM
- OP_CHANGE
- CASTING
- ADD_RETURN_VAL
- RENAME_VAR

`"involved_types"`: Indicates all type involved in this fix, including before and after fix. Composite types are broken down, e.g. `Union[int, str]` -> `"involved_types":["Union", "str", "int"]`.


`"type_change"`: Category of the type annotation change, which is one of the followings:
- ADDED
- REPLACED
- REMOVED

`"location"`: Location of the code change relative to the pyre warning message, which is one of the followings:
- ENCLOSING_FUN_RETURN
- ENCLOSING_FUN_PARAM
- ENCLOSING_FUN
- EXACT_LINE
- FUN_CALLEE

`"full_warning_msg"`: Warning message produced by pyre prior to the fix (i.e. the parent commit).

`"url"`: Url to the commit where this type fix happens. 

`"change_runtime"`: Boolean, `true` if the fix changes python runtime behavior.

`"mentioned_by_pyre"`: Boolean, `true` if the fixed (i.e. new) type annotation is mentioned in the pyre warning message. Some special cases:
- `true` if a subclass of the mentioned types is used
- `true` if `Optional[T]`/`None` is used when `None` is mentioned
- `true` if `Callable[T]` is used when the error type is Call error
- `true` if the new type can be represented by the mentioned types, e.g. true if `List[tuple[]]` is used when `List[Any]` is mentioned

# type_fix_code_data #
Contains old and new code from different type fixes. It is structured as `{repo}/{commit}/{old_code}` and `{repo}/{commit}/{new_code}`. Intermediate folders are kept. Downloaded by running `script_download_codes.py`.

# Output_type_fix_commits #
Contains commits that have less pyre type warnings than their parent commits. Used for selecting interesting commits to analyze.

It displays the warnings in both parent and child commits. Only warnings from *files that have a less number of warnings than parents* are shown. Generated from `script_AnalyzeRepos.py`.