import pytest

from tnl.lexer import Lexer
from tnl.parser import Parser
from tnl.code_printer import print_module_code


@pytest.mark.parametrize('src', [
    """
transform Test {
    headers {
        'a' -> 'AA'
        'B' -> 'BB'
        'C' -> 'CC'
    }
    values {
        ['AA'] -> {
            | add 1
            | mult 2
        }
        ['BB'] -> 999
        ['CC'] -> {
            | replace '  ' ' '
            | trim
        }
    }
}
    """,
])
def test_pretty_print_code(capsys, src):
    """
    Parse an already pretty printed src and ensure the result of pretty
    printing it is the same.
    """
    lexer = Lexer(src, 'test')
    tokens = lexer.lex()
    parser = Parser(tokens, 'test')
    ast = parser.parse()

    print_module_code(ast)

    captured = capsys.readouterr()
    assert captured.out.strip() == src.strip()
