import graphviz  # type: ignore
from _parser.ast_objects import *


class ASTVisualizer:
    def __init__(self, ast):
        self.ast = ast
        self.dot = graphviz.Digraph(comment="Abstract Syntax Tree (AST)")

    def visualize(self):
        for statement in self.ast:
            self.__visualize(statement)

        self.dot.render("graph.gv", view=True)

    def __visualize(self, expression):
        node_id = id(expression)
        if type(expression) == BinaryOperation:
            self.add_node(node_id, expression.op.value)

            if expression.left not in [Number, Boolean]:
                self.add_edge(node_id, id(expression.left))

            if expression.right not in [Number, Boolean]:
                self.add_edge(node_id, id(expression.right))

            self.__visualize(expression.left)
            self.__visualize(expression.right)
        elif type(expression) == Print:
            self.add_node(node_id, "print")
            for param in expression.params:
                self.add_edge(node_id, id(param))
                self.__visualize(param)
        elif type(expression) == AssignVariable:
            self.add_node(node_id, f"{expression.name.value} =")  # type: ignore
            self.add_edge(node_id, id(expression.value))
            self.__visualize(expression.value)
        else:
            self.add_node(id(expression), expression.token.value)

    def add_node(self, _id, label):
        self.dot.node(str(_id), str(label))

    def add_edge(self, start, end):
        self.dot.edge(str(start), str(end))
