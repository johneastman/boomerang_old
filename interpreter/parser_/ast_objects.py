import os
from functools import reduce
from random import random, randint, uniform
from typing import Callable

from interpreter.tokens.token import Token
from interpreter.tokens import tokens as t
from utils.utils import language_error, divide_by_zero_error, Platform, BOOMERANG_PLATFORM


class Expression:
    def __init__(self, line_num: int):
        self.line_num = line_num

    def __eq__(self, other: object) -> bool:
        raise Exception(f"__eq__ method in {type(self).__name__} not implemented.")

    def __str__(self) -> str:
        raise Exception(f"__str__ method in {type(self).__name__} not implemented.")

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        instance_vars = vars(self)

        return f"{class_name}({', '.join(list(map(lambda p: f'{p[0]}={repr(p[1])}', instance_vars.items())))})"

    def eq(self, other: "Expression") -> "Boolean":
        return Boolean(self.line_num, self == other)

    def ne(self, other: "Expression") -> "Boolean":
        return Boolean(self.line_num, not self.eq(other).value)

    def abs(self) -> "Expression":
        raise language_error(self.line_num, f"invalid type {type(self).__name__} for absolute value")

    def neg(self) -> "Expression":
        raise language_error(self.line_num, f"invalid type {type(self).__name__} for negation")

    def fac(self) -> "Expression":
        raise language_error(self.line_num, f"invalid type {type(self).__name__} for factorial")

    def inc(self) -> "Expression":
        raise language_error(self.line_num, f"invalid type {type(self).__name__} for increment")

    def dec(self) -> "Expression":
        raise language_error(self.line_num, f"invalid type {type(self).__name__} for decrement")

    def and_(self, other: object) -> "Expression":
        raise language_error(self.line_num,
                             f"Invalid types {type(self).__name__} and {type(other).__name__} for {t.AND}")

    def or_(self, other: object) -> "Expression":
        raise language_error(self.line_num,
                             f"invalid types {type(self).__name__} and {type(other).__name__} for {t.OR}")

    def xor(self, other: object) -> "Expression":
        raise language_error(self.line_num,
                             f"invalid types {type(self).__name__} and {type(other).__name__} for {t.XOR}")

    def contains(self, other: object) -> "Boolean":
        if isinstance(other, List):
            return Boolean(self.line_num, self in other.values)

        raise language_error(self.line_num,
                             f"invalid types {type(self).__name__} and {type(other).__name__} for {t.IN}")

    def gt(self, other: object) -> "Expression":
        raise language_error(self.line_num,
                             f"invalid types {type(self).__name__} and {type(other).__name__} for {t.GT}")

    def ge(self, other: object) -> "Expression":
        raise language_error(self.line_num,
                             f"invalid types {type(self).__name__} and {type(other).__name__} for {t.GE}")

    def lt(self, other: object) -> "Expression":
        raise language_error(self.line_num,
                             f"invalid types {type(self).__name__} and {type(other).__name__} for {t.LT}")

    def le(self, other: object) -> "Expression":
        raise language_error(self.line_num,
                             f"invalid types {type(self).__name__} and {type(other).__name__} for {t.LE}")

    def add(self, other: object) -> "Expression":
        raise language_error(self.line_num,
                             f"invalid types {type(self).__name__} and {type(other).__name__} for {t.PLUS}")

    def sub(self, other: object) -> "Expression":
        raise language_error(self.line_num,
                             f"invalid types {type(self).__name__} and {type(other).__name__} for {t.MINUS}")

    def mul(self, other: object) -> "Expression":
        raise language_error(self.line_num,
                             f"invalid types {type(self).__name__} and {type(other).__name__} for {t.MULTIPLY}")

    def div(self, other: object) -> "Expression":
        raise language_error(self.line_num,
                             f"invalid types {type(self).__name__} and {type(other).__name__} for {t.DIVIDE}")

    def mod(self, other: object) -> "Expression":
        raise language_error(self.line_num,
                             f"invalid types {type(self).__name__} and {type(other).__name__} for {t.MOD}")

    def pow(self, other: object) -> "Expression":
        raise language_error(self.line_num,
                             f"invalid types {type(self).__name__} and {type(other).__name__} for {t.PACK}")

    def ptr(self, other: object) -> "Expression":
        raise language_error(self.line_num,
                             f"invalid types {type(self).__name__} and {type(other).__name__} for {t.SEND}")

    def not_(self) -> "Expression":
        raise language_error(self.line_num, f"invalid type {type(self).__name__} for {t.NOT}")

    def pack(self) -> "Expression":
        raise language_error(self.line_num, f"invalid type {type(self).__name__} for {t.PACK}")

    def at(self, other: object) -> "Expression":
        raise language_error(self.line_num,
                             f"invalid types {type(self).__name__} and {type(other).__name__} for {t.INDEX}")


class Number(Expression):
    def __init__(self, line_num: int, value: float):
        super().__init__(line_num)
        self.value = value

    def __str__(self) -> str:
        return str(self.__display_value())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Number):
            return False
        return self.value == other.value

    def __display_value(self) -> float:
        if self.is_whole_number():
            return int(self.value)
        return self.value

    def abs(self) -> "Expression":
        return Number(self.line_num, abs(self.value))

    def neg(self) -> "Expression":
        return Number(self.line_num, -self.value)

    def fac(self) -> "Expression":
        if not self.is_whole_number():
            raise language_error(self.line_num, "expression for factorial must be whole number")

        base_number = int(self.value)

        if base_number == 0 or base_number == 1:
            return Number(self.line_num, 1)

        if base_number < 0:
            # For negative numbers, factorial is offset by 1 from its positive counterparts.
            # For example, -1! == 2!, -2! == 3!, -3! = 4!, etc.
            start_number = abs(base_number) + 1
        else:
            start_number = base_number

        # No need to start at 1 because 1 multiplied by anything is itself
        return Number(
            self.line_num,
            reduce(lambda a, b: a * b, [i for i in range(2, start_number + 1)])
        )

    def inc(self) -> "Expression":
        return Number(self.line_num, self.value + 1)

    def dec(self) -> "Expression":
        return Number(self.line_num, self.value - 1)

    def gt(self, other: object) -> "Expression":
        if isinstance(other, Number):
            return Boolean(self.line_num, self.value > other.value)
        return super().gt(other)

    def ge(self, other: object) -> "Expression":
        if isinstance(other, Number):
            return Boolean(self.line_num, self.value >= other.value)
        return super().ge(other)

    def lt(self, other: object) -> "Expression":
        if isinstance(other, Number):
            return Boolean(self.line_num, self.value < other.value)
        return super().lt(other)

    def le(self, other: object) -> "Expression":
        if isinstance(other, Number):
            return Boolean(self.line_num, self.value <= other.value)
        return super().le(other)

    def add(self, other: object) -> Expression:
        if isinstance(other, Number):
            return Number(self.line_num, self.value + other.value)

        return super().add(other)

    def sub(self, other: object) -> Expression:
        if isinstance(other, Number):
            return Number(self.line_num, self.value - other.value)

        return super().sub(other)

    def mul(self, other: object) -> Expression:
        if isinstance(other, Number):
            return Number(self.line_num, self.value * other.value)

        return super().mul(other)

    def div(self, other: object) -> Expression:
        if isinstance(other, Number):
            if other.value == 0:
                raise divide_by_zero_error(self.line_num)
            return Number(self.line_num, self.value / other.value)

        return super().div(other)

    def mod(self, other: object) -> "Expression":
        if isinstance(other, Number):
            if other.value == 0:
                raise divide_by_zero_error(self.line_num)
            return Number(self.line_num, self.value % other.value)

        return super().mod(other)

    def pow(self, other: object) -> "Expression":
        if isinstance(other, Number):
            return Number(self.line_num, self.value ** other.value)
        return super().pow(other)

    def is_whole_number(self) -> bool:
        """
        Originally used "self.value.is_integer()" but that caused this error:
            AttributeError: 'int' object has no attribute 'is_integer'

        To fix that error, I changed the code to "float(self.value).is_integer()", converting "self.value"
        to a float. However, that produced this error:
            OverflowError: int too large to convert to float
        """
        return self.value % 1 == 0


class String(Expression):
    def __init__(self, line_num: int, value: str):
        super().__init__(line_num)
        self.value = value

    def __str__(self) -> str:
        return f"\"{self.value}\""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, String):
            return False
        return self.value == other.value

    def add(self, other: object) -> Expression:
        if isinstance(other, String):
            return String(self.line_num, self.value + other.value)

        return super().add(other)


class Boolean(Expression):
    def __init__(self, line_num: int, value: bool):
        super().__init__(line_num)
        self.value = value

    def __str__(self) -> str:
        return t.get_token_literal("TRUE") if self.value else t.get_token_literal("FALSE")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Boolean):
            return False
        return self.value == other.value

    def not_(self) -> "Expression":
        return Boolean(self.line_num, not self.value)

    def and_(self, other: object) -> "Expression":
        if isinstance(other, Boolean):
            return Boolean(self.line_num, self.value and other.value)
        return super().and_(other)

    def or_(self, other: object) -> "Expression":
        if isinstance(other, Boolean):
            return Boolean(self.line_num, self.value or other.value)
        return super().or_(other)

    def xor(self, other: object) -> "Expression":
        if isinstance(other, Boolean):
            return Boolean(self.line_num, self.value != other.value)
        return super().xor(other)


class List(Expression):
    def __init__(self, line_num: int, values: list[Expression]):
        super().__init__(line_num)
        self.values = values

    def __str__(self) -> str:
        return f"({', '.join(map(str, self.values))})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, List):
            return False
        return self.values == other.values

    def neg(self) -> "Expression":
        values = list(reversed(self.values))
        return List(self.line_num, values)

    def pack(self) -> "Expression":
        return List(self.line_num, [List(self.line_num, self.values)])

    def ptr(self, other: object) -> "Expression":
        if isinstance(other, Expression):
            return List(self.line_num, self.values + [other])
        return super().ptr(other)

    def add(self, other: object) -> "Expression":
        if isinstance(other, List):
            return List(self.line_num, self.values + other.values)
        return super().add(other)

    def sub(self, other: object) -> "Expression":
        if isinstance(other, List):
            new_values = self.values
            for value_to_remove in other.values:
                new_values = [v for v in new_values if v.ne(value_to_remove).value]
            return List(self.line_num, new_values)

        return super().sub(other)

    def at(self, other: object) -> "Expression":
        if isinstance(other, Number):
            if not other.is_whole_number():
                raise language_error(self.line_num, "list index must be a whole number")

            if -len(self.values) <= other.value < len(self.values):
                return self.values[int(other.value)]

            raise language_error(self.line_num, f"list index {other} is out of range")

        return super().at(other)


class Function(Expression):
    def __init__(self, line_num: int, parameters: list["Identifier"], body: Expression):
        super().__init__(line_num)
        self.parameters = parameters
        self.body = body

    def __str__(self) -> str:
        return f"<function {hex(id(self))}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Function):
            return False
        return self.parameters == other.parameters and self.body == other.body

    def ptr(self, other: object) -> "Expression":
        if isinstance(other, List):
            return FunctionCall(self.line_num, self, other)
        return super().ptr(other)


class FunctionCall(Expression):
    def __init__(self, line_num: int, function: Function, call_params: List):
        super().__init__(line_num)
        self.function = function
        self.call_params = call_params

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FunctionCall):
            return False
        return self.function == other.function and self.call_params == other.call_params


class Identifier(Expression):
    def __init__(self, line_num: int, value: str):
        super().__init__(line_num)
        self.value = value

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Identifier):
            return False
        return self.value == other.value


class When(Expression):
    def __init__(self, line_num: int, expression: Expression, case_expressions: list[tuple[Expression, Expression]]):
        super().__init__(line_num)
        self.expression = expression
        self.case_expressions = case_expressions

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, When):
            return False
        return self.expression == other.expression and self.case_expressions == other.case_expressions

    def __str__(self) -> str:
        return f"<when {hex(id(self))}>"


class ForLoop(Expression):
    def __init__(
            self,
            line_num: int,
            element_identifier: str,
            values: Expression,
            conditional_expr: Expression,
            expression: Expression
    ) -> None:
        super().__init__(line_num)
        self.element_identifier = element_identifier
        self.values = values
        self.conditional_expr = conditional_expr
        self.expression = expression

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ForLoop):
            return False

        return self.element_identifier == other.element_identifier and self.values == other.values \
            and self.conditional_expr == other.conditional_expr and self.expression == other.expression

    def __str__(self) -> str:
        return f"<for {hex(id(self))}>"


class BuiltinFunction(Expression):
    print_ = "print"
    randint_ = "randint"
    randfloat = "randfloat"
    len_ = "len"
    range_ = "range"
    round_ = "round"
    input_ = "input"

    builtin_function_names = [
        print_,
        randint_,
        randfloat,
        len_,
        range_,
        round_,
        input_
    ]

    unsupported_platform = {
        input_: [Platform.WEB.name]
    }

    def __init__(self, line_num: int, name: str):
        super().__init__(line_num)
        self.name = name

    def __str__(self) -> str:
        return f"<built-in function {self.name}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BuiltinFunction):
            return False
        return self.name == other.name

    def ptr(self, other: object) -> "Expression":

        # Check if the builtin function is supported on the current platform
        platform = os.environ[BOOMERANG_PLATFORM]
        if platform in self.unsupported_platform.get(self.name, []):
            raise language_error(self.line_num, f"unsupported builtin function '{self.name}' for {platform} platform")

        if isinstance(other, List):
            function: Callable[[list[Expression]], Expression] | None = {
                self.print_: self.print,
                self.randint_: lambda args: self.random(args, False),
                self.randfloat: lambda args: self.random(args, True),
                self.len_: self.len,
                self.range_: self.range,
                self.round_: self.round,
                self.input_: self.input
            }.get(self.name, None)

            if function is None:
                raise Exception(f"Unimplemented builtin function {self.name}")
            return function(other.values)

        return super().ptr(other)

    def input(self, arguments: list[Expression]) -> String:

        if len(arguments) != 1:
            raise language_error(self.line_num, f"expected 1 argument, got {len(arguments)}")

        prompt = arguments[0]

        if not isinstance(prompt, String):
            raise language_error(
                self.line_num,
                f"unsupported type {type(prompt).__name__} for built-in function len"
            )

        value = input(prompt.value)

        return String(self.line_num, value)

    def len(self, arguments: list[Expression]) -> Number:
        if len(arguments) != 1:
            raise language_error(self.line_num, f"expected 1 argument, got {len(arguments)}")

        collection = arguments[0]

        if isinstance(collection, String):
            return Number(self.line_num, len(collection.value))
        elif isinstance(collection, List):
            return Number(self.line_num, len(collection.values))
        raise language_error(self.line_num, f"unsupported type {type(collection).__name__} for built-in function len")

    def print(self, arguments: list[Expression]) -> List:
        print(", ".join(map(str, arguments)))
        return List(self.line_num, arguments)

    def random(self, arguments: list[Expression], is_float: bool) -> Number:
        if is_float and len(arguments) == 0:
            return Number(self.line_num, random())
        elif len(arguments) == 1:
            start: Expression = Number(self.line_num, 0)
            end: Expression = arguments[0]
        elif len(arguments) == 2:
            start, end = arguments
        else:
            # randint accepts 1 or 2 arguments, whereas randfloat can accept 0 arguments to return a random number
            # between 0 and 1.
            num_args_str = "0, 1, or 2" if is_float else "1 or 2"
            raise language_error(
                self.line_num,
                f"incorrect number of arguments. Excepts {num_args_str} arguments, but got {len(arguments)}"
            )

        # Validate start value
        if not isinstance(start, Number):
            raise language_error(
                self.line_num,
                f"expected Number for start, got {type(start).__name__}"
            )

        if not is_float and not start.is_whole_number():
            raise language_error(self.line_num, f"start must be a whole number")

        # Validate end value
        if not isinstance(end, Number):
            raise language_error(
                self.line_num,
                f"expected Number for end, got {type(end).__name__}"
            )

        if not is_float and not end.is_whole_number():
            raise language_error(self.line_num, f"end must be a whole number")

        # Ensure start value is less than end value
        if end.value < start.value:
            raise language_error(
                self.line_num,
                f"end ({str(end)}) must be greater than start ({str(start)})"
            )

        return Number(
            self.line_num,
            uniform(start.value, end.value) if is_float else randint(int(start.value), int(end.value))
        )

    def range(self, arguments: list[Expression]) -> List:
        if len(arguments) == 1:
            start: Expression = Number(self.line_num, 0)
            end: Expression = arguments[0]
            step: Expression = Number(self.line_num, 1)
        elif len(arguments) == 2:
            start, end = arguments
            step = Number(self.line_num, 1)
        elif len(arguments) == 3:
            start, end, step = arguments
        else:
            raise language_error(
                self.line_num,
                f"incorrect number of arguments. Excepts 1, 2, or 3 arguments, but got {len(arguments)}"
            )

        # Validate start value
        if not isinstance(start, Number):
            raise language_error(
                self.line_num,
                f"expected Number for start, got {type(start).__name__}"
            )

        # Validate end value
        if not isinstance(end, Number):
            raise language_error(
                self.line_num,
                f"expected Number for end, got {type(end).__name__}"
            )

        # Validate step value
        if not isinstance(step, Number):
            raise language_error(
                self.line_num,
                f"expected Number for step, got {type(step).__name__}"
            )

        if step.value == 0:
            raise language_error(
                self.line_num,
                f"step cannot be 0"
            )

        # Make sure step value is correct for start and end. If "start" is greater than "end" but "step" is positive,
        # raise an error. Similarly, if "start" is less than "end" but "step" is negative, raise an error.
        if start.value > end.value and step.value > 0:
            raise language_error(
                self.line_num,
                f"step value must be negative if start value is greater than end value"
            )
        elif start.value < end.value and step.value < 0:
            raise language_error(
                self.line_num,
                f"step value must be positive if start value is less than end value"
            )

        # If "start" is less than "end", generate numbers in ascending order. Otherwise, if "start" is
        # greater than "end", generate numbers in descending order.
        is_within_range: Callable[[float, float], bool] = \
            (lambda a, b: a < b) if start.value < end.value else (lambda a, b: a > b)

        # Generate the range
        values: list[Expression] = []
        next_value = start.value
        while is_within_range(next_value, end.value):
            values.append(Number(self.line_num, next_value))
            next_value += step.value

        return List(self.line_num, values)

    def round(self, arguments: list[Expression]) -> Number:
        if len(arguments) != 2:
            raise language_error(
                self.line_num,
                f"incorrect number of arguments. Excepts 2 arguments, but got {len(arguments)}"
            )

        number, round_to = arguments

        if not isinstance(number, Number):
            raise language_error(
                self.line_num,
                f"expected Number for number, got {type(number).__name__}"
            )

        if not isinstance(round_to, Number):
            raise language_error(
                self.line_num,
                f"expected Number for round_to, got {type(round_to).__name__}"
            )

        if not round_to.is_whole_number():
            raise language_error(self.line_num, "round_to must be a whole number")

        if round_to.value < 0:
            raise language_error(self.line_num, "round_to must be greater than or equal to 0")

        return Number(
            self.line_num,
            round(number.value, int(round_to.value))
        )


class PrefixExpression(Expression):
    def __init__(self, line_num: int, operator: Token, expression: Expression):
        super().__init__(line_num)
        self.operator = operator
        self.expression = expression

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PrefixExpression):
            return False
        return self.operator == other.operator and self.expression == other.expression


class InfixExpression(Expression):
    def __init__(self, line_num: int, left: Expression, operator: Token, right: Expression):
        super().__init__(line_num)
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InfixExpression):
            return False
        return self.left == other.left and self.operator == other.operator and self.right == other.right


class PostfixExpression(Expression):
    def __init__(self, line_num: int, operator: Token, expression: Expression):
        super().__init__(line_num)
        self.operator = operator
        self.expression = expression

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PostfixExpression):
            return False
        return self.operator == other.operator and self.expression == other.expression


class Assignment(Expression):
    def __init__(self, line_num: int, name: str, value: Expression):
        super().__init__(line_num)
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Assignment):
            return False
        return self.name == other.name and self.value == other.value


class Error(Expression):
    def __init__(self, line_num: int, message: str):
        super().__init__(line_num)
        self.message = message

    def __str__(self) -> str:
        return self.message

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Error):
            return False
        return self.message == other.message
