import pytest

from tnl.lexer import Lexer
from tnl.parser import Parser
from tnl.semantic_analyzer import SemanticAnalyzer


@pytest.mark.parametrize('src,expected_error_message', [
    pytest.param(
        '''
transform T {
    headers {
        'hello' -> hello 'world'
    }
}
        ''',
        'Unrecognized map \'hello\'.',
        id='unrecognized_map',
    ),
    pytest.param(
        '''
transform T {
    headers {
        'hello' -> format ' {planet'
    }
}
        ''',
        'Invalid format string (expected \'}\' before end of string).',
        id='invalid_format_string',
    ),
    pytest.param(
        '''
transform T {
    headers {
        # would likely need to be /.*/
        /*/ -> 'world'
    }
}
        ''',
        'Invalid regex pattern /*/.',
        id='invalid_pattern',
    ),
])
def test_pretty_print_code(capsys, src, expected_error_message):
    lexer = Lexer(src, 'test')
    tokens = lexer.lex()
    parser = Parser(tokens, 'test')
    try:
        ast = parser.parse()
        analyzer = SemanticAnalyzer(ast)
        errors = analyzer.analyze()

        assert len(errors) == 1

        print(errors[0])
    except SystemExit:  # this is because the parser currently exits on error
        pass

    captured = capsys.readouterr()
    assert expected_error_message.strip() in captured.out.strip()
