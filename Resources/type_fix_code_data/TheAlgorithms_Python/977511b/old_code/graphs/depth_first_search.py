"""Non recursive implementation of a DFS algorithm."""

from __future__ import annotations


def depth_first_search(graph: dict, start: str) -> set[int]:
    """Depth First Search on Graph
    :param graph: directed graph in dictionary format
    :param vertex: starting vertex as a string
    :returns: the trace of the search
    >>> G = { "A": ["B", "C", "D"], "B": ["A", "D", "E"],
    ... "C": ["A", "F"], "D": ["B", "D"], "E": ["B", "F"],
    ... "F": ["C", "E", "G"], "G": ["F"] }
    >>> start = "A"
    >>> output_G = list({'A', 'B', 'C', 'D', 'E', 'F', 'G'})
    >>> all(x in output_G for x in list(depth_first_search(G, "A")))
    True
    >>> all(x in output_G for x in list(depth_first_search(G, "G")))
    True
    """
    explored, stack = set(start), [start]

    while stack:
        v = stack.pop()
        explored.add(v)
        # Differences from BFS:
        # 1) pop last element instead of first one
        # 2) add adjacent elements to stack without exploring them
        for adj in reversed(graph[v]):
            if adj not in explored:
                stack.append(adj)
    return explored


G = {
    "A": ["B", "C", "D"],
    "B": ["A", "D", "E"],
    "C": ["A", "F"],
    "D": ["B", "D"],
    "E": ["B", "F"],
    "F": ["C", "E", "G"],
    "G": ["F"],
}

if __name__ == "__main__":
    import doctest

    doctest.testmod()
    print(depth_first_search(G, "A"))
