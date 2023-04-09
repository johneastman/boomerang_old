from interpreter.parser_.parser_ import Parser
from interpreter.tokens.tokenizer import Tokenizer
from interpreter.tokens.token_queue import TokenQueue


def parser(source: str) -> Parser:
    tokenizer = Tokenizer(source)
    tokens = TokenQueue(tokenizer)
    return Parser(tokens)
