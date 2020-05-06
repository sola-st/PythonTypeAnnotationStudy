from typing import Any

def process_something(arguments: Any) -> int:
    pass


from typing import List, Tuple

def foo2(l: Tuple[str]) -> int:
    pass

def goo(t: List[str, ...]) -> int:
    pass

from typing import Optional

def foo1(s: Optional[str]) -> int:
    pass