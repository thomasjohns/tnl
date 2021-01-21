import sys

from proto.lexer import Lexer


_, src_file, csv_file = sys.argv

with open(src_file, "r") as fp:
    src = fp.read()

lexer = Lexer(src, src_file)
tokens = lexer.lex()

print(src)
for token in tokens:
    print(token)
