import typing

from interpreter._parser import _parser
from interpreter._parser.ast_objects import BinaryExpression, UnaryExpression, Identifier, Number, String, Assignment, \
    Error, Boolean
from interpreter.tokens.tokens import *
from interpreter.evaluator._environment import Environment
from interpreter.utils.utils import language_error, LanguageRuntimeException
import copy


class Evaluator:
    def __init__(self, ast: list[_parser.Expression], env: typing.Optional[Environment]) -> None:
        self.ast = ast
        self.env = env

    @property
    def get_env(self) -> Environment:
        if self.env is None:
            raise Exception("Environment is None")
        return self.env

    def evaluate(self) -> typing.List[_parser.Expression]:
        try:
            return self.evaluate_statements(self.ast)
        except LanguageRuntimeException as e:
            return [Error(e.line_num, str(e))]

    def evaluate_statements(self, statements: list[_parser.Expression]) -> list[_parser.Expression]:
        evaluated_expressions = []
        for expression in statements:
            evaluated_expression = self.evaluate_expression(expression)
            # `copy.deepcopy` ensures each evaluated expression in `evaluated_expressions` is accurate to the state of
            # the program during the evaluation of that particular expression.
            evaluated_expressions.append(copy.deepcopy(evaluated_expression))

        # TODO: Figure out how to handle returns for both REPL and regular code execution
        return evaluated_expressions

    def evaluate_expression(self, expression: _parser.Expression) -> _parser.Expression:

        if isinstance(expression, BinaryExpression):
            return self.evaluate_binary_expression(expression)

        elif isinstance(expression, UnaryExpression):
            return self.evaluate_unary_expression(expression)

        elif isinstance(expression, Assignment):
            return self.evaluate_assign_variable(expression)

        elif isinstance(expression, Identifier):
            return self.evaluate_identifier(expression)

        # Base Types
        elif isinstance(expression, Number):
            return expression

        elif isinstance(expression, String):
            return expression

        elif isinstance(expression, Boolean):
            return expression

        # This is a program-specific error because a missing object type would come about during development, not
        # when a user is using this programming language.
        raise Exception(f"Unsupported type: {type(expression).__name__}")

    def evaluate_assign_variable(self, variable: _parser.Assignment) -> _parser.Expression:
        var_value: _parser.Expression = self.evaluate_expression(variable.value)
        self.get_env.set_var(variable.variable, var_value)
        return var_value

    def evaluate_identifier(self, identifier: _parser.Identifier) -> _parser.Expression:
        # For variables, check the current environment. If it does not exist, check the parent environment.
        # Continue doing this until there are no more parent environments. If the variable does not exist in all
        # scopes, it does not exist anywhere in the code.
        env: typing.Optional[Environment] = self.env
        while env is not None:
            variable_value = env.get_var(identifier.value)
            if variable_value is not None:

                # When a variable is retrieved, update the line number to reflect the current line number because the
                # variable was saved with the line number where it was defined.
                variable_value.line_num = identifier.line_num
                return variable_value
            env = env.parent_env

        raise language_error(identifier.line_num, f"undefined variable: {identifier.value}")

    def evaluate_unary_expression(self, unary_expression: _parser.UnaryExpression) -> _parser.Expression:
        expression_result = self.evaluate_expression(unary_expression.expression)
        op = unary_expression.operator

        if op.type == PLUS:
            if isinstance(expression_result, Number):
                new_value = abs(float(expression_result.value))
                return _parser.Number(expression_result.line_num, new_value)

        elif op.type == MINUS:
            if isinstance(expression_result, Number):
                new_value = -float(expression_result.value)
                return _parser.Number(expression_result.line_num, new_value)

        raise Exception(f"Invalid unary operator: {op.type} ({op.value})")

    def evaluate_binary_expression(self, binary_operation: _parser.BinaryExpression) -> _parser.Expression:
        left = self.evaluate_expression(binary_operation.left)

        right = self.evaluate_expression(binary_operation.right)
        op = binary_operation.operator

        # Math operations
        if op.type == PLUS:
            return left + right

        elif op.type == MINUS:
            return left - right

        elif op.type == MULTIPLY:
            return left * right

        elif op.type == DIVIDE:
            return left / right

        raise language_error(op.line_num, f"Invalid binary operator '{op.value}'")
