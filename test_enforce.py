import unittest

from enforce import ContractEnforcementViolation
from enforce import ContractSignatureViolation
from enforce import enforce


def better_be(x):
    return lambda y: x == y


class TestEnforce(unittest.TestCase):
    def test_enforce_errors_with_invalid_argument(self):
        def some_method(a, b):
            pass

        with self.assertRaises(ContractSignatureViolation):
            decorator = enforce("c")
            decorator(some_method)

    def test_enforce_errors_with_failed_contract(self):
        @enforce("a", lambda x: x == "a")
        def some_method(a):
            pass

        with self.assertRaises(ContractEnforcementViolation):
            some_method("b")

    def test_enforce_with_kwargs(self):
        @enforce("a", better_be("a"))
        @enforce("b", better_be("b"))
        @enforce("c", better_be(("c",)))
        @enforce("d", better_be("d"))
        @enforce("e", better_be("e"))
        @enforce("f", better_be({"f": "f"}))
        def some_method(a, b="b", *c, d, e="e", **f):
            return True

        self.assertTrue(some_method("a", "b", "c", d="d", e="e", f="f"))
        self.assertTrue(some_method("a", "b", "c", d="d", f="f"))

    def test_enforce_uses_defaults(self):
        @enforce("a", better_be(1))
        def some_method(a=1):
            return True

        self.assertTrue(some_method())

    def test_enforce_enforces_return(self):
        @enforce("return", better_be(True))
        def some_method():
            return True

        self.assertTrue(some_method())

        @enforce("return", better_be(False))
        def some_method():
            return True

        with self.assertRaises(ContractEnforcementViolation):
            some_method()

    def test_multiple_enforce_side_effects(self):
        self.call_count = 0

        @enforce("return", better_be(True))
        @enforce("return", lambda x: True)
        def some_method():
            self.call_count += 1
            return True

        some_method()
        self.assertEqual(self.call_count, 1)
        some_method()
        self.assertEqual(self.call_count, 2)
