import sys
import warnings

# ignore pandas lzma warning
warnings.simplefilter(action='ignore', category=UserWarning)
import pandas as pd  # type: ignore

from tablang.lexer import Lexer
from tablang.parser import Parser
from tablang.ast_printer import print_module_ast
from tablang.code_printer import print_module_code
from tablang.vm import transform

_, src_file, csv_file = sys.argv

with open(src_file, "r") as fp:
    src = fp.read()

print(src)

lexer = Lexer(src, src_file)
tokens = lexer.lex()

for token in tokens:
    print(token)
print()

parser = Parser(tokens, src_file)
ast = parser.parse()

print_module_ast(ast)
print()
print_module_code(ast)
print()

df = pd.read_csv(csv_file)
print(df.to_csv(index=False))

df = transform(ast, df)

print(df.to_csv(index=False))
