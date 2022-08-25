import pytest

from _parser._parser import Parser
from _parser.ast_objects import *
from tokens.tokenizer import Token


def test_set_statement():
    tokens = [
        Token("set", SET, 1),
        Token("variable", IDENTIFIER, 1),
        Token("=", ASSIGN, 1),
        Token("1", INTEGER, 1),
        Token(";", SEMICOLON, 1),
    ]

    p = Parser(tokens)
    actual_assign_ast = p.assign()
    expected_assign_ast = SetVariable(
        Identifier("variable", 1),
        Integer(1, 1))
    assert actual_assign_ast == expected_assign_ast


operate_assign_tests = [
    ("+=", ASSIGN_ADD, "+", PLUS),
    ("-=", ASSIGN_SUB, "-", MINUS),
    ("*=", ASSIGN_MUL, "*", MULTIPLY),
    ("/=", ASSIGN_DIV, "/", DIVIDE),
]


@pytest.mark.parametrize("operator_assign_literal, operator_assign_type, operator_literal, operator_type", operate_assign_tests)
def test_set_statement_operate_assign(operator_assign_literal, operator_assign_type, operator_literal, operator_type):
    variable_name = "variable"
    identifier_token = Identifier(variable_name, 1)
    tokens = [
        Token("set", SET, 1),
        Token(variable_name, IDENTIFIER, 1),
        Token(operator_assign_literal, operator_assign_type, 1),
        Token("1", INTEGER, 1),
        Token(";", SEMICOLON, 1),
    ]

    p = Parser(tokens)
    actual_assign_ast = p.assign()
    expected_assign_ast = SetVariable(
        identifier_token,
        BinaryOperation(
            identifier_token,
            Token(operator_literal, operator_type, 1),
            Integer(1, 1)))

    assert actual_assign_ast == expected_assign_ast


def test_loop():
    tokens = [
        Token("while", WHILE, 1),
        Token("i", IDENTIFIER, 1),
        Token("<", LT, 1),
        Token("10", INTEGER, 1),
        Token("{", OPEN_CURLY_BRACKET, 1),
        Token("set", SET, 2),
        Token("i", IDENTIFIER, 2),
        Token("+=", ASSIGN_ADD, 2),
        Token("1", INTEGER, 2),
        Token(";", SEMICOLON, 2),
        Token("}", CLOSED_CURLY_BRACKET, 3),
        Token(";", SEMICOLON, 3),
    ]

    p = Parser(tokens)
    actual_loop_ast = p.loop()
    expected_loop_ast = Loop(
        BinaryOperation(Identifier("i", 1), Token("<", LT, 1), Integer(10, 1)),
        [
            SetVariable(Identifier("i", 2),
                        BinaryOperation(Identifier("i", 2), Token("+", PLUS, 2), Integer(1, 2)))
        ]
    )

    assert actual_loop_ast == expected_loop_ast
