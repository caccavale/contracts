import inspect
from functools import wraps
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Tuple
from typing import Union

from more_itertools import partition

from predicates import strings_before_callables


class ContractViolation(TypeError):
    pass


class ContractSignatureViolation(ContractViolation):
    pass


class ContractEnforcementViolation(ContractViolation):
    pass


def _partition(
    arguments: Iterable[Union[str, Callable]]
) -> Tuple[List[str], List[Callable]]:
    arg_names, predicates = partition(lambda arg: isinstance(arg, Callable), arguments)
    return list(arg_names), list(predicates)


def _get_args(
    args: List, kwargs: Dict, original_method, argument_names: List[str]
) -> List:
    called_arguments = inspect.getcallargs(original_method, *args, **kwargs)
    return [called_arguments[argument_name] for argument_name in argument_names]


def _arg_spec_contains(arg_spec, argument) -> bool:
    return (
        argument in arg_spec.args
        or argument == arg_spec.varargs
        or argument in arg_spec.kwonlyargs
        or argument == arg_spec.varkw
    )


def _without(ls: List, i: int) -> List:
    return [l for l in ls if l != i]


def enforce(*args: Union[str, Callable]):
    if not strings_before_callables(args):
        raise ContractSignatureViolation(
            "All string arguments to enforce must come before all predicates."
        )

    # ['a', 'b', pred1, pred2] -> ('a', 'b'), (pred1, pred2)
    arg_names, predicates = _partition(args)

    def decorator(method):
        original_method = method.inner if hasattr(method, "inner") else method
        arg_spec = inspect.getfullargspec(original_method)

        # A workaround for closure behavior
        argument_names = arg_names if arg_names else arg_spec.args

        for arg_name in argument_names:
            if arg_name != "return" and not _arg_spec_contains(arg_spec, arg_name):
                raise ContractSignatureViolation(
                    f"{method.__name__} does not have argument: {arg_name}"
                )

        @wraps(method)
        def wrapper(*fargs, **fkwargs):
            arguments = list(fargs)
            keyword_arguments = dict(fkwargs)

            returns = None
            if "return" in argument_names:
                returns = method(*fargs, **fkwargs)

                return_index = argument_names.index("return")

                predicate_args = _get_args(
                    arguments,
                    keyword_arguments,
                    original_method,
                    _without(argument_names, "return"),
                )
                predicate_args.insert(return_index, returns)

            else:
                predicate_args = _get_args(
                    arguments, keyword_arguments, original_method, argument_names
                )

            for predicate in predicates:
                if not predicate(*predicate_args):
                    raise ContractEnforcementViolation(
                        f"Contract violation: {predicate.__name__}"
                        f"({dict(zip(argument_names, predicate_args))} failed."
                    )

            return returns if returns is not None else method(*fargs, **fkwargs)

        setattr(wrapper, "inner", original_method)

        return wrapper

    return decorator
