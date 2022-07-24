from tokens.tokenizer import Token
from typing import Optional


class Statement:
    pass


class Expression(Statement):
    pass


class BooleanExpression(Expression):
    pass


class AdditionExpression(BooleanExpression):
    pass


class Term(AdditionExpression):
    pass


class Factor(Term):
    pass


class ExpressionStatement(Statement):
    def __init__(self, expr: Expression):
        self.expr = expr

    def __eq__(self, other: object):
        if not isinstance(other, ExpressionStatement):
            return False
        return self.expr == other.expr


class Base:
    """Base class for lowest-level objects in the abstract syntax tree.

    Data types line integers, floats, booleans, strings, etc., but also identifiers (variables, functions, etc.)
    """
    def __init__(self, token: Token):
        self.token = token

    def __eq__(self, other: object):
        if not isinstance(other, self.__class__):
            return False
        return self.token == other.token

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"{class_name}(token={self.token})"


class BuiltinFunction(Factor):

    def __init__(self, params: list[Expression], line_num: int):
        self.params = params
        self.line_num = line_num

    def __eq__(self, other: object):
        if not isinstance(other, BuiltinFunction):
            return False
        return self.params == other.params and self.line_num == other.line_num

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"{class_name}({self.params}, {self.line_num})"


class Print(BuiltinFunction):
    def __init__(self, params: list[Expression], line_num: int):
        super().__init__(params, line_num)


class Type(BuiltinFunction):
    def __init__(self, params: list[Expression], line_num: int):
        super().__init__(params, line_num)


class Random(BuiltinFunction):
    def __init__(self, params: list[Expression], line_num: int):
        super().__init__(params, line_num)


class Number(Base, Factor):
    def __init__(self, token: Token):
        super().__init__(token)


class Float(Base, Factor):
    def __init__(self, token: Token):
        super().__init__(token)


class Boolean(Base, Factor):
    def __init__(self, token: Token):
        super().__init__(token)


class String(Base, Factor):
    def __init__(self, token: Token):
        super().__init__(token)


class Identifier(Base, Factor):
    def __init__(self, token: Token):
        super().__init__(token)


class Dictionary(Factor):
    def __init__(self, keys, values, line_num):
        self.keys = keys
        self.values = values
        self.line_num = line_num

    def __eq__(self, other):
        if not isinstance(other, Dictionary):
            return False
        return self.keys == other.keys and self.values == other.values

    def __repr__(self):
        return f"Dictionary(keys={self.keys}, values={self.values})"


class NoReturn(Token):
    def __init__(self, line_num: int = 0):
        super().__init__("", "", line_num)

    def __eq__(self, other):
        if not isinstance(other, NoReturn):
            return False
        return self.value == other.value and self.type == other.type and self.line_num == other.line_num


class Index(Expression):
    def __init__(self, left: Expression, index: Expression):
        self.left = left
        self.index = index

    def __eq__(self, other: object):
        if not isinstance(other, Index):
            return False
        return self.left == other.left and self.index == other.index

    def __repr__(self):
        return f"Index(left={self.left}, index={self.index})"


class Return(Statement):
    def __init__(self, expr: Expression):
        self.expr = expr

    def __repr__(self):
        return f"[{self.__class__.__name__}(value={self.expr})]"


class Loop(Statement):
    def __init__(self, condition: Expression, statements: list[Statement]):
        self.condition = condition
        self.statements = statements

    def __repr__(self):
        return f"[{self.__class__.__name__}(condition: {self.condition}, statements: {self.statements})]"


class AssignFunction(Statement):
    def __init__(self, name: Token, parameters, statements):
        self.name = name
        self.parameters = parameters
        self.statements = statements

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"{class_name}(parameters={self.parameters}, statements={self.statements})"


class IfStatement(Statement):
    def __init__(self,
                 comparison: Expression,
                 true_statements: list[Statement],
                 false_statements: Optional[list[Statement]]):

        self.comparison = comparison
        self.true_statements = true_statements
        self.false_statements = false_statements


class FunctionCall(Factor):
    def __init__(self, name: Token, parameter_values):
        self.name = name
        self.parameter_values = parameter_values

    def __repr__(self):
        return f"[{self.__class__.__name__}(name={self.name}, parameter_values={self.parameter_values})]"


class BinaryOperation(Expression):
    def __init__(self, left: Expression, op: Token, right: Expression):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"[{class_name}(left={self.left}, op={self.op}, right={self.right})]"

    def __eq__(self, other):
        if not isinstance(other, BinaryOperation):
            return False

        return self.left == other.left and self.op == other.op and self.right == other.right


class AssignVariable(Statement):
    def __init__(self, name: Token, value: Expression):
        self.name = name
        self.value = value

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"{class_name}(name={self.name}, value={self.value})"


class UnaryOperation(Factor):
    def __init__(self, op: Token, expression):
        self.op = op
        self.expression = expression

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"[{class_name}(op={self.op}, expression={self.expression})]"
