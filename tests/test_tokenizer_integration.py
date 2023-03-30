import pytest
from tokens.tokens import *
from tokens.tokenizer import Tokenizer, Token

data_types_tests = [
    ("\"hello, world!\"", [
        Token("hello, world!", STRING, 1),
        Token("", EOF, 1)
    ]),
    ("true", [
        Token("true", BOOLEAN, 1),
        Token("", EOF, 1)
    ]),
    ("false", [
        Token("false", BOOLEAN, 1),
        Token("", EOF, 1)
    ]),
    ("1", [
        Token("1", INTEGER, 1),
        Token("", EOF, 1)
    ]),
    ("15", [
        Token("15", INTEGER, 1),
        Token("", EOF, 1)
    ]),
    ("153", [
        Token("153", INTEGER, 1),
        Token("", EOF, 1)
    ]),
    ("1.5", [
        Token("1.5", FLOAT, 1),
        Token("", EOF, 1)
    ]),
]


@pytest.mark.parametrize("source,expected_tokens", data_types_tests)
def test_data_types(source, expected_tokens):
    actual_tokens = get_tokens(source)
    assert actual_tokens == expected_tokens


tokenizer_tests = [
    ("1 + 1;", [
        Token("1", INTEGER, 1),
        Token("+", PLUS, 1),
        Token("1", INTEGER, 1),
        Token(";", SEMICOLON, 1),
        Token("", EOF, 1)
    ]),
    ("a = 1;\nb = 2;", [
        Token("a", IDENTIFIER, 1),
        Token("=", ASSIGN, 1),
        Token("1", INTEGER, 1),
        Token(";", SEMICOLON, 1),
        Token("b", IDENTIFIER, 2),
        Token("=", ASSIGN, 2),
        Token("2", INTEGER, 2),
        Token(";", SEMICOLON, 2),
        Token("", EOF, 2)
    ]),
    ("# a = 1;\nb = 2;", [
        Token("b", IDENTIFIER, 2),
        Token("=", ASSIGN, 2),
        Token("2", INTEGER, 2),
        Token(";", SEMICOLON, 2),
        Token("", EOF, 2)
    ]),
    ("\n/*x = 1;\nb = 2; */\nc = 3;", [
        Token("c", IDENTIFIER, 4),
        Token("=", ASSIGN, 4),
        Token("3", INTEGER, 4),
        Token(";", SEMICOLON, 4),
        Token("", EOF, 4)
    ]),
    ("/*func is_eq(a, b) {\n    return a == b;\n};\n*/print(1 / 1);", [
        Token("print", IDENTIFIER, 4),
        Token("(", OPEN_PAREN, 4),
        Token("1", INTEGER, 4),
        Token("/", DIVIDE, 4),
        Token("1", INTEGER, 4),
        Token(")", CLOSED_PAREN, 4),
        Token(";", SEMICOLON, 4),
        Token("", EOF, 4)
    ])
]


@pytest.mark.parametrize("source, expected_tokens", tokenizer_tests)
def test_tokenizer(source, expected_tokens):
    actual_tokens = get_tokens(source)
    assert actual_tokens == expected_tokens


def get_tokens(source: str) -> list[Token]:
    return [t for t in Tokenizer(source)]
