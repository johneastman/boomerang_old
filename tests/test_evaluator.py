import unittest
from tokens.tokens import *
from tokens.tokenizer import Token, Tokenizer
from _parser import Parser, NoReturn
from evaluator import Evaluator
from _environment import Environment


class TestEvaluator(unittest.TestCase):

    def test_evaluator(self):
        tests = [
            ("1 + 1;", [Token(2, NUMBER, 1)]),
            ("1 + 2 * 2;", [Token(5, NUMBER, 1)]),
            ("(1 + 2) * 2;", [Token(6, NUMBER, 1)]),
            ("let x = (1 + 2) * 2;x;", [NoReturn(), Token(6, NUMBER, 1)]),
            ("4 / 2;", [Token(2.0, NUMBER, 1)]),
            ("7 / 2;", [Token(3.5, NUMBER, 1)])
        ]
        self.run_tests(tests)

    def test_boolean_operators(self):
        tests = [
            ("1 == 1;", [Token("true", BOOLEAN, 1)]),
            ("1 != 1;", [Token("false", BOOLEAN, 1)]),
            ("1 != 2;", [Token("true", BOOLEAN, 1)]),
            ("1 >= 1;", [Token("true", BOOLEAN, 1)]),
            ("1 >= 2;", [Token("false", BOOLEAN, 1)]),
            ("1 > 1;",  [Token("false", BOOLEAN, 1)]),
            ("2 > 1;",  [Token("true", BOOLEAN, 1)]),
            ("1 <= 1;", [Token("true", BOOLEAN, 1)]),
            ("1 < 2;",  [Token("true", BOOLEAN, 1)]),
            ("2 < 1;",  [Token("false", BOOLEAN, 1)]),
            ("10 == (2 + 4 * 2) == true;",  [Token("true", BOOLEAN, 1)]),
        ]
        self.run_tests(tests)

    def test_invalid_boolean_operators(self):
        tests = [
            ("1 == true;", "NUMBER", "EQ", "BOOLEAN"),
            ("1 != true;", "NUMBER", "NE", "BOOLEAN"),
            ("1 > true;", "NUMBER", "GT", "BOOLEAN"),
            ("2 >= false;", "NUMBER", "GE", "BOOLEAN"),
            ("2 < false;", "NUMBER", "LT", "BOOLEAN"),
            ("2 <= false;", "NUMBER", "LE", "BOOLEAN"),

            # Check that we can't use boolean operators in less-than, greater-than, greater-than-or-equal, or
            # less-than-or-equal
            ("true <= false;", "BOOLEAN", "LE", "BOOLEAN"),
            ("true < false;", "BOOLEAN", "LT", "BOOLEAN"),
            ("true >= false;", "BOOLEAN", "GE", "BOOLEAN"),
            ("true > false;", "BOOLEAN", "GT", "BOOLEAN"),
        ]

        for source, left_type, operation_type, right_type in tests:
            with self.subTest(source):
                with self.assertRaises(Exception) as error:
                    self.actual_result(source)
                self.assertEqual(
                    f"Cannot perform {operation_type} operation on {left_type} and {right_type}",
                    str(error.exception))

    def test_valid_unary_operators(self):
        tests = [
            ("-1;", [
                Token(-1, NUMBER, 1)
             ]),
            ("+1;", [
                Token(1, NUMBER, 1)
            ]),
            ("!true;", [
                Token("false", BOOLEAN, 1)
            ]),
            ("!false;", [
                Token("true", BOOLEAN, 1)
            ]),
        ]
        self.run_tests(tests)

    def test_invalid_unary_operators(self):
        tests = [
            ("!1;", "BANG", "NUMBER"),
            ("-true;", "MINUS", "BOOLEAN"),
            ("-false;", "MINUS", "BOOLEAN"),
            ("+true;", "PLUS", "BOOLEAN"),
            ("+false;", "PLUS", "BOOLEAN"),
        ]

        for source, op, _type in tests:
            with self.subTest(source):
                with self.assertRaises(Exception) as error:
                    self.actual_result(source)
                self.assertEqual(
                    f"Cannot perform {op} operation on {_type}",
                    str(error.exception)
                )

    def test_function_return(self):
        source = """
        func is_equal(a, b) {
            if (a == b) {
                return true;
            };
        };
        is_equal(1, 1);  # true
        is_equal(1, 2);  # No return
        """
        expected_results = [
            NoReturn(),
            Token("true", BOOLEAN, 7),
            NoReturn(),
        ]
        actual_results = self.actual_result(source)
        self.assert_tokens_equal(expected_results, actual_results)

    def test_variable_assignment(self):
        tests = [
            ("let a = 2; a += 2; a;", [
                NoReturn(),
                NoReturn(),
                Token(4, NUMBER, 1)
            ]),
            ("let a = 2; a -= 2; a;", [
                NoReturn(),
                NoReturn(),
                Token(0, NUMBER, 1)
            ]),
            ("let a = 2; a *= 2; a;", [
                NoReturn(),
                NoReturn(),
                Token(4, NUMBER, 1)
            ]),
            ("let a = 2; a /= 2; a;", [
                NoReturn(),
                NoReturn(),
                Token(1, NUMBER, 1)
            ])
        ]
        self.run_tests(tests)

    def run_tests(self, tests):
        for source, expected_results in tests:
            with self.subTest(source):
                actual_results = self.actual_result(source)
                self.assert_tokens_equal(expected_results, actual_results)

    def assert_tokens_equal(self, expected_results, actual_results):
        self.assertEqual(len(expected_results), len(actual_results))

        for expected, actual in zip(expected_results, actual_results):
            self.assertEqual(expected.value, actual.value)
            self.assertEqual(expected.type, actual.type)
            self.assertEqual(expected.line_num, actual.line_num)

    def actual_result(self, source):
        t = Tokenizer(source)
        tokens = t.tokenize()

        p = Parser(tokens)
        ast = p.parse()

        e = Evaluator(ast, Environment())
        return e.evaluate()


if __name__ == "__main__":
    unittest.main()
