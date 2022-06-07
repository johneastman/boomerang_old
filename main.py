from tokenizer import Tokenizer
from _parser import Parser
from evaluator import Evaluator
from _environment import Environment
from _ast import AST

PROMPT = ">> "


def get_source(filepath):
    with open(filepath, "r") as file:
        return file.read()


def repl():

    env = Environment(None)

    while True:
        _input = input(PROMPT)

        if _input.lower() == "exit":
            break
        else:
            try:
                t = Tokenizer(_input)
                tokens = t.tokenize()

                p = Parser(tokens)
                ast = p.parse()

                e = Evaluator(ast, env)
                result = e.evaluate()
                print(result)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    env = Environment()
    visualize = False

    source = get_source("language.txt")
    t = Tokenizer(source)
    tokens = t.tokenize()

    p = Parser(tokens)
    ast = p.parse()

    e = Evaluator(ast, env)
    e.evaluate()

    if visualize:
        AST(ast).visualize()
