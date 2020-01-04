from typing import Callable
from typing import List
from typing import Sequence
from typing import Type
from typing import Union


def collection_ordered_by_type(collection: Sequence, *types: Type) -> bool:
    index = 0
    for t in types:
        while index < len(collection) and isinstance(collection[index], t):
            index += 1
    return index == len(collection)


def strings_before_callables(items: Sequence[Union[str, Callable]]) -> bool:
    return collection_ordered_by_type(items, str, Callable)


def homogeneous_type(items: Sequence):
    if len(items) <= 1:
        return True
    return sequence_of_type(items[1:], type(items[0]))


def sequence_of_type(items: Sequence, t: Type) -> bool:
    return all(isinstance(item, t) for item in items)


def is_sorted(numbers: List[int]) -> bool:
    return all(a == b for a, b in zip(numbers, sorted(numbers)))


def equal_length(*args) -> bool:
    return all(len(args[0]) == len(a) for a in args[1:])
