import io

import pandas as pd  # type: ignore
import pytest

from tnl.lexer import Lexer
from tnl.parser import Parser
from tnl.vm import transform


@pytest.mark.parametrize('src,input_data_str,expected_result_data_str', [
    (
        '''\
transform Test {
    headers {
        'a' -> 'AA' | replace 'A' 'D'
        'B' -> 'BB'
        'C' -> 'CC'
    }
    values {
        ['DD'] -> add 1 | mult 2
        ['BB'] -> 999
        ['CC'] -> {
            | replace '  ' ' '
            | trim
        }
    }
}
        ''',
        '''\
a,B,C
1,2, hello world
1,2,Hello World
1,2,hello  world
        ''',
        '''\
DD,BB,CC
4,999,hello world
4,999,Hello World
4,999,hello world
        ''',
    ),
])
def test_interpret(
    src: str,
    input_data_str: str,
    expected_result_data_str: str,
) -> None:
    lexer = Lexer(src, 'test')
    tokens = lexer.lex()
    parser = Parser(tokens, 'test')
    ast = parser.parse()

    data = pd.read_csv(io.StringIO(input_data_str.strip()))

    transformed_data = transform(ast, data)

    output_buffer = io.StringIO()
    transformed_data.to_csv(output_buffer, index=False)
    output_buffer.seek(0)
    result_data_str = output_buffer.read()

    assert result_data_str.strip() == expected_result_data_str.strip()
