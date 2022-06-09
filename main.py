from tokenizer import Tokenizer
from _parser import Parser
from evaluator import Evaluator
from _environment import Environment
from ast_visualizer import ASTVisualizer

PROMPT = ">> "


def get_source(filepath):
    with open(filepath, "r") as file:
        return file.read()


def evaluate(source, environment, visualize=False):

    t = Tokenizer(source)
    tokens = t.tokenize()

    p = Parser(tokens)
    ast = p.parse()

    if visualize:
        ASTVisualizer(ast).visualize()

    e = Evaluator(ast, environment)
    return e.evaluate()


def repl():
    env = Environment()
    while True:
        _input = input(PROMPT)

        if _input.lower() == "exit":
            break
        else:
            try:
                evaluated_expressions = evaluate(_input, env)
                print(" ".join(map(str, [token.value for token in evaluated_expressions])))
            except Exception as e:
                print(e)


if __name__ == "__main__":
    # source = get_source("language.txt")
    # evaluate(source, Environment())
    repl()
