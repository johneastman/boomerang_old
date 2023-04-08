import typing
from interpreter.tokens.tokenizer import Token
from interpreter.tokens.token_queue import TokenQueue
from interpreter._parser.ast_objects import *
from interpreter.tokens.tokens import *
from interpreter.utils.utils import language_error

# Precedence names
LOWEST = "LOWEST"  # default
SUM = "SUM"  # +, -
PRODUCT = "PRODUCT"  # *, /


class Parser:

    def __init__(self, tokens: TokenQueue):
        self.tokens = tokens

        self.assignment_operators: list[str] = [
            ASSIGN
        ]

        # Higher precedence is lower on the list (for example, && and || take precedence above everything, so they have
        # a precedence level of 2.
        #
        # Storing the precedence levels in this list allows precedences to be rearranged without having to manually
        # change other precedence values. For example, if we want to add a precedence before EDGE, we can just add it
        # to this list, and the parser will automatically handle that precedence's integer value (which is the
        # index + 1).
        self.precedences: list[str] = [
            LOWEST,
            SUM,
            PRODUCT
        ]

        self.infix_precedence: dict[str, str] = {
            PLUS: SUM,
            MINUS: SUM,
            MULTIPLY: PRODUCT,
            DIVIDE: PRODUCT,
        }

    def parse(self) -> list[Expression]:
        return self.parse_statements(EOF)

    def parse_statements(self, end_type: str) -> list[Expression]:
        """Parse statements within a certain scope (set by 'end_type')

        For block statements, that value will be a closed curly bracket. For program statements, that value will be an
        end-of-file token.
        """
        statements = []
        while self.current.type != end_type:
            statements.append(self.expression())
            self.is_expected_token(SEMICOLON)
            self.advance()
        return statements

    def advance(self) -> None:
        self.tokens.next()

    @property
    def peek(self) -> Token:
        return self.tokens.peek()

    @property
    def current(self) -> Token:
        return self.tokens.current

    def get_precedence_level(self, precedence_name: str) -> int:
        """Get the precedence level of a given precedence. The precedences are stores in 'self.precedences' from lowest
        to highest, so the precedence value is just the index + 1, where LOWEST is 1.

        :param precedence_name: precedence name/label (see top of this file above Parser class)
        :return: the precedence level
        """
        return self.precedences.index(precedence_name) + 1

    def get_next_precedence_level(self, precedence_dict: dict[str, str]) -> int:
        """Get the precedence level of the next operator in the expression.

        :param precedence_dict: token-precedence mapping for the next token in the expression
        :return: precedence level for token type in 'precedence_dict'
        """
        precedence_name = precedence_dict.get(self.current.type, LOWEST)
        return self.get_precedence_level(precedence_name)

    def expression(self, precedence_name: str = LOWEST) -> Expression:
        precedence_level = self.get_precedence_level(precedence_name)

        # Prefix
        left = self.parse_prefix()

        # Infix
        while self.current is not None and precedence_level < self.get_next_precedence_level(self.infix_precedence):
            left = self.parse_infix(left)

        return left

    def parse_prefix(self) -> Expression:

        if self.current.type == IDENTIFIER and self.peek.type == ASSIGN:
            return self.assign()

        if self.current.type in [MINUS, PLUS]:
            op = self.current
            self.advance()
            expression = self.expression()
            return UnaryExpression(op.line_num, op, expression)

        elif self.current.type == OPEN_PAREN:
            self.advance()
            expression = self.expression()
            if self.current.type == CLOSED_PAREN:
                self.advance()
                return expression
            self.is_expected_token(CLOSED_PAREN)

        elif self.current.type == NUMBER:
            number_token = self.current
            self.advance()
            return Number(number_token.line_num, float(number_token.value))

        elif self.current.type == STRING:
            string_token = self.current
            self.advance()
            return String(string_token.line_num, string_token.value)

        elif self.current.type == BOOLEAN:
            boolean_token = self.current
            self.advance()
            return Boolean(
                boolean_token.line_num,
                True if boolean_token.value == get_token_literal("TRUE") else False
            )

        elif self.current.type == IDENTIFIER:
            identifier_token = self.current
            self.advance()
            return Identifier(identifier_token.line_num, identifier_token.value)

        raise language_error(self.current.line_num, f"Invalid token: {self.current.type} ({self.current.value})")

    def parse_infix(self, left: Expression) -> Expression:
        op = self.current
        self.advance()
        right = self.expression(self.infix_precedence.get(op.type, LOWEST))
        return BinaryExpression(op.line_num, left, op, right)

    def assign(self) -> Expression:
        self.is_expected_token(IDENTIFIER)
        variable_name = self.current

        # Skip over assignment operator
        self.advance()

        self.is_expected_token(self.assignment_operators)

        self.advance()
        right = self.expression()

        return Assignment(variable_name.line_num, variable_name.value, right)

    def add_semicolon(self) -> None:
        self.tokens.add("SEMICOLON")

    def is_expected_token(self, expected_token_type: typing.Union[str, list[str]]) -> None:

        # Multiple token types may be expected, so a list of tokens types can be passed. If just a string is passed,
        # that string will be added to a list
        expected_token_types = [expected_token_type] if isinstance(expected_token_type, str) else expected_token_type

        if self.current.type not in expected_token_types:
            raise language_error(
                self.current.line_num,
                f"Expected {expected_token_type}, got {self.current.type} ('{self.current.value}')")
