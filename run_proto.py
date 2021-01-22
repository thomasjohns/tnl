import sys

from proto.lexer import Lexer
from proto.parser import Parser
from proto.pretty_printer import print_module


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
