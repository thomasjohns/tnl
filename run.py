import sys

from tablang.lexer import Lexer
from tablang.parser import Parser
from tablang.pretty_printer import print_module


_, src_file, csv_file = sys.argv

with open(src_file, "r") as fp:
    src = fp.read()

lexer = Lexer(src, src_file)
tokens = lexer.lex()
parser = Parser(tokens, src_file)
ast = parser.parse()

print(src)

for token in tokens:
    print(token)

print_module(ast)
