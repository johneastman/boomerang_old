import typing

from _parser import _parser
from tokens.tokens import *
from evaluator._environment import Environment
from utils.utils import raise_error, ReturnException
import copy
import random


class Evaluator:
    def __init__(self, ast, env):
        self.ast = ast
        self.env = env

        # Map operations to valid data types. This ensures expressions like "1 + true", "!1", "-true", "+false", etc.
        # are invalid.
        self.valid_operation_types = {
            PLUS: [_parser.Integer, _parser.String, _parser.Float],
            MINUS: [_parser.Integer, _parser.Float],
            MULTIPLY: [_parser.Integer, _parser.Float],
            DIVIDE: [_parser.Integer, _parser.Float],
            EQ: [_parser.Integer, _parser.Boolean, _parser.Float, _parser.String],
            NE: [_parser.Integer, _parser.Boolean, _parser.Float, _parser.String],
            GT: [_parser.Integer, _parser.Float],
            GE: [_parser.Integer, _parser.Float],
            LT: [_parser.Integer, _parser.Float],
            LE: [_parser.Integer, _parser.Float],
            BANG: [_parser.Boolean],
            AND: [_parser.Boolean],
            OR: [_parser.Boolean]
        }

        # Map what types are compatible with others when performing operations (for example, addition can be performed
        # on floats and integers).
        self.compatible_types_for_operations = {
            _parser.Float: [_parser.Float, _parser.Integer],
            _parser.Integer: [_parser.Integer, _parser.Float],
            _parser.String: [_parser.String],
            _parser.Boolean: [_parser.Boolean]
        }

    def evaluate(self):
        return self.evaluate_statements(self.ast)

    def evaluate_statements(self, statements: list[_parser.Statement]):
        evaluated_expressions = []
        for expression in statements:
            evaluated_expression = self.evaluate_expression(expression)
            # `copy.deepcopy` ensures each evaluated expression in `evaluated_expressions` is accurate to the state of
            # the program during the evaluation of that particular expression.
            evaluated_expressions.append(copy.deepcopy(evaluated_expression))

            if isinstance(expression, _parser.Return):
                # Raise an exception for returns so that in the case of early returns (e.g., a return in an if-else
                # block), the rest of the AST below that return block is ignored. Without throwing an exception,
                # the following code would return "false" instead of "true", which is the expected return value.
                # ```
                # if 1 == 1 {
                #     return true;
                # };
                # return false;
                # ```
                raise ReturnException(evaluated_expression)

        # TODO: Figure out how to handle returns for both REPL and regular code execution
        if len(evaluated_expressions) == 0:
            return _parser.NoReturn()
        return evaluated_expressions

    def validate_expression(self, expression):
        value: _parser.Base = self.evaluate_expression(expression)
        if isinstance(value, _parser.NoReturn):
            raise_error(value.line_num, "cannot evaluate expression that returns no value")
        return value

    def evaluate_expression(self, expression: typing.Union[_parser.Expression, _parser.Statement]) -> _parser.Base:
        if isinstance(expression, _parser.BinaryOperation):
            return self.evaluate_binary_expression(expression)

        elif isinstance(expression, _parser.UnaryOperation):
            return self.evaluate_unary_expression(expression)

        elif isinstance(expression, _parser.IfStatement):
            return self.evaluate_if_statement(expression)

        elif isinstance(expression, _parser.SetVariable):
            return self.evaluate_assign_variable(expression)

        elif isinstance(expression, _parser.AssignFunction):
            return self.evaluate_assign_function(expression)

        elif isinstance(expression, _parser.Identifier):
            return self.evaluate_identifier(expression)

        elif isinstance(expression, _parser.FunctionCall):
            return self.evaluate_function_call(expression)

        elif isinstance(expression, _parser.Loop):
            return self.evaluate_loop_statement(expression)

        elif isinstance(expression, _parser.Print):
            return self.evaluate_print_statement(expression)

        elif isinstance(expression, _parser.AddNode):
            return self.evaluate_add_node(expression)

        elif isinstance(expression, _parser.Factorial):
            return self.evaluate_factorial(expression)

        elif isinstance(expression, _parser.Return):
            return self.validate_expression(expression.expr)

        elif isinstance(expression, _parser.ExpressionStatement):
            return self.evaluate_expression(expression.expr)

        elif isinstance(expression, _parser.ToType):
            return self.evaluate_to_string(expression)

        # Base Types
        elif isinstance(expression, _parser.Random):
            return _parser.Float(random.random(), expression.line_num)

        elif isinstance(expression, _parser.Integer):
            return expression

        elif isinstance(expression, _parser.Float):
            return expression

        elif isinstance(expression, _parser.Boolean):
            return expression

        elif isinstance(expression, _parser.String):
            return expression

        elif isinstance(expression, _parser.Tree):
            return self.evaluate_tree(expression)

        # This is a program-specific error because a missing object type would come about during development, not
        # when a user is using this programming language.
        raise Exception(f"Unsupported type: {type(expression).__name__}")

    def evaluate_to_string(self, to_type: _parser.ToType) -> _parser.Base:
        base_object: _parser.Base = self.evaluate_expression(to_type.params[0])
        conversion_type: typing.Optional[typing.Type[_parser.Base]] = to_type.get_language_type()

        if conversion_type is None:
            raise Exception(f"Unsupported Python type: {to_type.type.__name__}")

        if isinstance(base_object, conversion_type):
            # If the object passed to "to_string" is already a string, just return the object
            return base_object
        return conversion_type(to_type.type(base_object), to_type.line_num)

    def evaluate_add_node(self, add_node: _parser.AddNode) -> _parser.NoReturn:

        if len(add_node.params) != add_node.num_params:
            raise_error(add_node.line_num, f"Incorrect number of arguments. Expected {add_node.num_params}, got {len(add_node.params)}")

        # mypy error: Incompatible types in assignment (expression has type "Base", variable has type "Tree")
        # reason for ignore: if "tree" is not a "Tree" object, an exception will be thrown
        tree: _parser.Tree = self.evaluate_expression(add_node.params[0])  # type: ignore
        if not isinstance(tree, _parser.Tree):
            raise_error(add_node.line_num, f"Invalid type {tree.__class__.__name__} for add_node")

        value = self.evaluate_expression(add_node.params[1])
        add_path = self.evaluate_expression(add_node.params[2])
        tree.add_node(_parser.Node(value), str(add_path.value))
        return _parser.NoReturn(line_num=add_node.line_num)

    def evaluate_tree(self, tree: _parser.Tree) -> _parser.Tree:
        # Iterate through the tree to evaluate and update each node's value
        #
        # mypy error: Incompatible types in assignment (expression has type "Union[int, str, float, Node, None]",
        #             variable has type "Node")
        # reason for ignore: "Node" in "Union[int, str, float, Node, None]"
        root: _parser.Node = tree.value  # type: ignore

        def traverse(node: _parser.Node):
            # mypy error: Incompatible types in assignment (expression has type "Base", variable has type "Expression")
            # reason for ignore: TODO: fix type
            node.value = self.evaluate_expression(node.value)  # type: ignore
            for child in node.children:
                traverse(child)

        traverse(root)
        return _parser.Tree(root, tree.line_num)

    def evaluate_factorial(self, factorial_expression: _parser.Factorial) -> _parser.Integer:
        result: _parser.Base = self.evaluate_expression(factorial_expression.expr)

        if not isinstance(result, _parser.Integer):
            raise_error(result.line_num, f"Invalid type {type(result)} for factorial")

        new_val = 1

        # mypy error: No overload variant of "range" matches argument types "object", "int", "int"
        # reason for ignore: "result.value" is an integer
        for i in range(result.value, 1, -1):  # type: ignore
            new_val *= i
        return _parser.Integer(new_val, result.line_num)

    def evaluate_assign_variable(self, variable_assignment: _parser.SetVariable) -> _parser.NoReturn:
        variable = variable_assignment.name

        if isinstance(variable, _parser.Identifier):
            var_value: _parser.Base = self.validate_expression(variable_assignment.value)
            self.env.set_var(variable.value, var_value)
            return _parser.NoReturn(line_num=var_value.line_num)

        raise_error(variable_assignment.name.line_num, f"cannot assign value to type {variable.__class__.__name__}")

    def evaluate_assign_function(self, function_definition: _parser.AssignFunction) -> _parser.Base:
        self.env.set_func(function_definition.name.value, function_definition)
        return _parser.NoReturn(line_num=function_definition.name.line_num)

    def evaluate_identifier(self, identifier: _parser.Identifier) -> _parser.Base:
        # For variables, check the current environment. If it does not exist, check the parent environment.
        # Continue doing this until there are no more parent environments. If the variable does not exist in all
        # scopes, it does not exist anywhere in the code.
        env = self.env
        while env is not None:
            variable_value = env.get_var(identifier.value)
            if variable_value is not None:

                # When a variable is retrieved, update the line number to reflect the current line number because the
                # variable was saved with the line number where it was defined.
                variable_value.line_num = identifier.line_num
                return variable_value
            env = env.parent_env

        raise_error(identifier.line_num, f"undefined variable: {identifier.value}")

    def evaluate_function_call(self, function_call: _parser.FunctionCall) -> _parser.Base:
        function_name = function_call.name.value

        function: typing.Optional[_parser.AssignFunction] = None
        env = self.env
        while env is not None:
            f = env.get_func(function_call.name.value)
            if f is not None:
                function = f
            env = env.parent_env

        # If the function is not defined in the functions dictionary, throw an error saying the
        # function is undefined
        if function is None:
            raise_error(function_call.name.line_num, f"Undefined function: {function_name}")

        parameter_identifiers = function.parameters
        parameter_values = function_call.parameter_values

        if len(parameter_identifiers) != len(parameter_values):
            error_msg = "Incorrect number of arguments. "
            error_msg += f"Function '{function_name}' defined with {len(parameter_identifiers)} parameters "
            error_msg += f"({', '.join(map(lambda t: t.value, parameter_identifiers))}), "
            error_msg += f"but {len(parameter_values)} given."
            raise_error(function_call.name.line_num, error_msg)

        # Map the parameters to their values and set them in the variables dictionary
        evaluated_param_values = {}
        for param_name, param_value in zip(parameter_identifiers, parameter_values):
            evaluated_param_values[param_name.value] = self.validate_expression(param_value)

        # Create a new environment for the function's variables
        self.env = Environment(parent_env=self.env)
        self.env.set_vars(evaluated_param_values)

        # Evaluate every expression in the function body
        statements = function.statements

        try:
            # If a ReturnException is never thrown, then the function does not return anything.
            self.evaluate_statements(statements)
            return _parser.NoReturn(line_num=function_call.name.line_num)
        except ReturnException as return_exception:
            # If a ReturnException is thrown, return the value of the evaluated expression in the return statement
            return_token = return_exception.token
            return_token.line_num = function_call.name.line_num
            return return_token
        finally:
            # After the function is called, switch to the parent environment
            self.env = self.env.parent_env

    def evaluate_loop_statement(self, loop: _parser.Loop) -> _parser.Base:
        while self.validate_expression(loop.condition).value is True:
            self.evaluate_statements(loop.statements)
        return _parser.NoReturn()

    def evaluate_if_statement(self, if_statement: _parser.IfStatement) -> _parser.Base:
        evaluated_comparison = self.validate_expression(if_statement.comparison)

        # We don't need to return the results of the 'if' or 'else' blocks because an if-statement has no return value
        if evaluated_comparison.value is True:
            self.evaluate_statements(if_statement.true_statements)
        elif if_statement.false_statements is not None:
            self.evaluate_statements(if_statement.false_statements)
        return _parser.NoReturn()

    def evaluate_print_statement(self, _print: _parser.Print) -> _parser.Base:
        evaluated_params = []
        for param in _print.params:
            result = self.validate_expression(param)
            evaluated_params.append(str(result))
        print(" ".join(evaluated_params))
        return _parser.NoReturn(line_num=_print.line_num)

    def evaluate_unary_expression(self, unary_expression: _parser.UnaryOperation) -> _parser.Base:
        expression_result = self.validate_expression(unary_expression.expression)
        expression_result_type = type(expression_result)
        op_type = unary_expression.op.type

        valid_type = self.valid_operation_types.get(op_type, [])

        # mypy error: Unsupported right operand type for in ("object")
        # reason for ignore: TODO: investigate
        if expression_result_type not in valid_type:  # type: ignore
            raise_error(expression_result.line_num, f"Cannot perform {op_type} operation on {expression_result_type.__name__}")

        if op_type == PLUS:
            actual_value = expression_result.value
            actual_type = self.get_type(actual_value)
            return actual_type(actual_value, expression_result.line_num)
        elif op_type == MINUS:
            actual_value = -expression_result.value
            actual_type = self.get_type(actual_value)
            return actual_type(actual_value, expression_result.line_num)
        elif op_type == BANG:
            actual_value = not expression_result.value
            actual_type = self.get_type(actual_value)
            return actual_type(actual_value, expression_result.line_num)
        else:
            raise Exception(f"Invalid unary operator: {op_type} ({unary_expression.op.value})")

    def evaluate_binary_expression(self, binary_operation: _parser.BinaryOperation) -> _parser.Base:
        left = self.validate_expression(binary_operation.left)
        left_type = type(left)

        right = self.validate_expression(binary_operation.right)
        right_type = type(right)
        op_type = binary_operation.op.type

        # Check that the types are compatible. If they are not, the operation cannot be performed.
        #
        # Without this check, someone could run "1 == true" or "false != 2". Both checks are technically valid, but
        # this is invalid because the data types for the left and right expressions are not compatible. However,
        # to account for the fact that some expressions can result in different data types (e.g., two integers resulting
        # in a float, like 3 / 4), we need to allow operations to happen on compatible data types, like floats and
        # integers.
        #
        # mypy error: Incompatible types in assignment (expression has type "object", variable has type "List[Base]")
        # reason for ignore: TODO: investigate
        left_compatible_types: list[_parser.Base] = self.compatible_types_for_operations.get(left_type, [])  # type: ignore
        right_compatible_types: list[_parser.Base] = self.compatible_types_for_operations.get(right_type, [])  # type: ignore

        if left_type not in right_compatible_types or right_type not in left_compatible_types:
            raise raise_error(left.line_num, f"Cannot perform {op_type} operation on {left_type.__name__} and {right_type.__name__}")

        # Check that the operation can be performed on the given types. For example, "true > false" is not valid
        #
        # mypy error: Incompatible types in assignment (expression has type "object", variable has type "List[Base]")
        # reason for ignore: TODO: investigate
        valid_type: list[_parser.Base] = self.valid_operation_types.get(op_type, [])  # type: ignore
        if left_type not in valid_type or right_type not in valid_type:
            raise raise_error(left.line_num, f"Cannot perform {op_type} operation on {left_type.__name__} and {right_type.__name__}")

        # Math operations
        if op_type == PLUS:
            result = left.value + right.value
            result_type = self.get_type(result)
            return result_type(result, left.line_num)
        elif op_type == MINUS:
            result = left.value - right.value
            result_type = self.get_type(result)
            return result_type(result, left.line_num)
        elif op_type == MULTIPLY:
            result = left.value * right.value
            result_type = self.get_type(result)
            return result_type(result, left.line_num)
        elif op_type == DIVIDE:
            if right.value == 0:
                raise Exception("Division by zero")
            result = left.value / right.value
            result_type = self.get_type(result)
            return result_type(result, left.line_num)

        # Binary comparisons
        elif op_type == EQ:
            result = left.value == right.value
            return _parser.Boolean(result, left.line_num)
        elif op_type == NE:
            result = left.value != right.value
            return _parser.Boolean(result, left.line_num)
        elif op_type == GT:
            result = left.value > right.value
            return _parser.Boolean(result, left.line_num)
        elif op_type == GE:
            result = left.value >= right.value
            return _parser.Boolean(result, left.line_num)
        elif op_type == LT:
            result = left.value < right.value
            return _parser.Boolean(result, left.line_num)
        elif op_type == LE:
            result = left.value <= right.value
            return _parser.Boolean(result, left.line_num)
        elif op_type == AND:
            result = left.value and right.value
            return _parser.Boolean(result, left.line_num)
        elif op_type == OR:
            result = left.value or right.value
            return _parser.Boolean(result, left.line_num)
        else:
            raise Exception(f"Invalid binary operator '{binary_operation.op.value}' at line {binary_operation.op.line_num}")

    def get_type(self, value: object):
        if type(value) == bool:
            return _parser.Boolean
        if type(value) == float:
            return _parser.Float
        elif type(value) == int:
            return _parser.Integer
        else:
            return _parser.String
