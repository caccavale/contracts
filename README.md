# contracts

## Example

```python
@enforce("a", is_sorted)
@enforce("b", is_sorted)
@enforce("return", is_sorted)
@enforce("a", "b", "return", equal_length)
def sorted_safe_zip(a: List[A], b: List[B]) -> List[Tuple[A, B]]:
    return list(zip(a, b))
```