import pytest

from tnl.lexer import Lexer
from tnl.parser import Parser
from tnl.code_printer import print_module_code


@pytest.mark.parametrize('src', [
    pytest.param(
        '''
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
        ''',
        id='parse_integration_test_1',
    ),
    pytest.param(
        '''
transform Test {
    headers {
        'idx' -> 'Idx'
        'Year-Month-Day' -> slice 0 4
    }
    values {
        'Year' -> slice 0 4
    }
}
        ''',
        id='parse_integration_test_2',
    ),
    pytest.param(
        '''\
transform Test {
    headers {
        /(\s+.*)|(.*\s+)/ -> trim
    }
}
        ''',
        id='parse_header_pattern',
    ),
    pytest.param(
        '''\
transform Test {
    values {
        [/upp*./] -> upper
    }
}
        ''',
        id='parse_values_pattern',
    ),
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
