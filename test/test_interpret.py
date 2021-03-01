import io

import pandas as pd  # type: ignore
import pytest

from tnl.lexer import Lexer
from tnl.parser import Parser
from tnl.vm import transform


@pytest.mark.parametrize('src,input_data_str,expected_result_data_str', [
    pytest.param(
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
        id='interpret_integration_test_1',
    ),
    pytest.param(
        '''\
transform Movies {
    headers {
        'date' -> 'Year'
        'name' -> 'Title'
        'producer' -> 'Producer(s)'
    }

    values {
        ['Year'] -> slice 0 4
        ['Title'] -> trim | title | replace 'Of' 'of'
        ['Producer(s)'] -> {
            | trim
            | replace ';' ','
            | replace_last ',' ', and'
        }
    }
}
        ''',
        '''\
date,name,producer
2019-10-5, parasite ,Kwak Sin-ae; Bong Joon-ho
2018-09-11, green book ,Jim Burke; Charles B. Wessler; Brian Currie; Peter Farrelly; Nick V.
2017-08-31, the shape of water ,Guillermo del Toro; J. Miles Dale
2016-09-02, moonlight ,Adele Romanski; Dede Gardner; Jeremy Kleiner
        ''',
        '''\
Year,Title,Producer(s)
2019,Parasite,"Kwak Sin-ae, and Bong Joon-ho"
2018,Green Book,"Jim Burke, Charles B. Wessler, Brian Currie, Peter Farrelly, and Nick V."
2017,The Shape of Water,"Guillermo del Toro, and J. Miles Dale"
2016,Moonlight,"Adele Romanski, Dede Gardner, and Jeremy Kleiner"
        ''',
        id='interpret_integration_test_example_from_readme',
    ),
    pytest.param(
        '''\
transform Test {
    headers {
        'idx' -> 'Idx'
        'Year-Month-Day' -> slice 0 4
    }
    values {
        ['Year'] -> slice 0 4
    }
}
        ''',
        '''\
idx,Year-Month-Day
1,2020-01-01
2,2019-02-15
3,2017-08-02
        ''',
        '''\
Idx,Year
1,2020
2,2019
3,2017
        ''',
        id='slice',
    ),
    pytest.param(
        '''\
transform Test {
    headers {
        'idx' -> title
        'message' -> title
    }
    values {
        ['Message'] -> title
    }
}
        ''',
        '''\
idx,message
1,hello world
2,hello mars
3,hello andromeda
        ''',
        '''\
Idx,Message
1,Hello World
2,Hello Mars
3,Hello Andromeda
        ''',
        id='title',
    ),
    pytest.param(
        '''\
transform Test {
    headers {
        'a;b;c' -> {
            | replace ';' '; '
            | replace_last '; ' '; and '
        }
    }
    values {
        ['a; b; and c'] -> replace_last 'a' 'b'
    }
}
        ''',
        '''\
idx,a;b;c
1,aaaabac
2,aabc
        ''',
        '''\
idx,a; b; and c
1,aaaabbc
2,abbc
        ''',
        id='replace_last',
    ),
    pytest.param(
        '''\
transform Test {
    headers {
        'planet' -> format '{} greeting'
    }
    values {
        [/.*planet.*/] -> format 'hello {}'
    }
}
        ''',
        '''\
idx,planet
1,earth
2,mars
        ''',
        '''\
idx,planet greeting
1,hello earth
2,hello mars
        ''',
        id='format',
    ),
    pytest.param(
        '''\
transform Test {
    headers {
        /(\\s+.*)|(.*\\s+)/ -> trim
    }
}
        ''',
        '''\
 a , b , c,d
1,2,3,4
5,6,7,8
        ''',
        '''\
a,b,c,d
1,2,3,4
5,6,7,8
        ''',
        id='header_pattern_1',
    ),
    pytest.param(
        '''\
transform Test {
    headers {
        /b|d/ -> upper
    }
}
        ''',
        '''\
a,b,c,d
1,2,3,4
5,6,7,8
        ''',
        '''\
a,B,c,D
1,2,3,4
5,6,7,8
        ''',
        id='header_pattern_2',
    ),
    pytest.param(
        '''\
transform Test {
    headers {
        /.*/ -> trim
        /b|d/ -> upper
    }
}
        ''',
        '''\
a, b   , c, d
1,2,3,4
5,6,7,8
        ''',
        '''\
a,B,c,D
1,2,3,4
5,6,7,8
        ''',
        id='header_pattern_3',
    ),
    pytest.param(
        '''\
transform Test {
    values {
        [/upp*./] -> upper
    }
}
        ''',
        '''\
lower,upper
hello,world
hello,mars
        ''',
        '''\
lower,upper
hello,WORLD
hello,MARS
        ''',
        id='values_pattern',
    ),
    pytest.param(
        '''\
transform Test {
    values {
        ['a'] -> True
        ['b'] -> False
    }
}
        ''',
        '''\
a,b
1,2
3,4
        ''',
        '''\
a,b
True,False
True,False
        ''',
        id='true_and_false_tokens',
    ),
    pytest.param(
        '''\
transform Test {
    headers {
        'B' -> lower
    }
    values {
        ['b'] -> lower
    }
}
        ''',
        '''\
A,B
HELLO,WORLD
HELLO,MARS
        ''',
        '''\
A,b
HELLO,world
HELLO,mars
        ''',
        id='lower',
    ),
    pytest.param(
        '''\
transform Test {
    headers {
        'noisea' -> remove_prefix 'noise'
    }
    values {
        ['a'] -> remove_prefix 'noise'
    }
}
        ''',
        '''\
noisea,b
noisehello,world
noisehello,mars
        ''',
        '''\
a,b
hello,world
hello,mars
        ''',
        id='remove_prefix',
    ),
    pytest.param(
        '''\
transform Test {
    headers {
        'anoise' -> remove_suffix 'noise'
    }
    values {
        ['a'] -> remove_suffix 'noise'
    }
}
        ''',
        '''\
anoise,b
hellonoise,world
hellonoise,mars
        ''',
        '''\
a,b
hello,world
hello,mars
        ''',
        id='remove_suffix',
    ),
    pytest.param(
        '''\
transform Test {
    headers {
        'placeholder' -> concat 'hello' ' ' 'message'
    }
    values {
        ['hello message'] -> concat ['a'] ' ' ['b']
    }
}
        ''',
        '''\
a,b,placeholder
hello,world,placeholder
hello,mars,placeholder
        ''',
        '''\
a,b,hello message
hello,world,hello world
hello,mars,hello mars
        ''',
        id='concat',
    ),
    pytest.param(
        '''\
transform Test {
    values {
        ['b'] -> power 3
    }
}
        ''',
        '''\
a,b
1,2
3,4
        ''',
        '''\
a,b
1,8
3,64
        ''',
        id='power',
    ),
    pytest.param(
        '''\
transform Test {
    values {
        ['b'] -> divide 2
    }
}
        ''',
        '''\
a,b
1,2
3,4
        ''',
        '''\
a,b
1,1
3,2
        ''',
        id='divide',
    ),
    pytest.param(
        '''\
transform Test {
    values {
        ['idx'] -> auto_inc
    }
}
        ''',
        '''\
idx,a,b
placeholder,1,2
placeholder,3,4
placeholder,5,6
placeholder,7,8
        ''',
        '''\
idx,a,b
1,1,2
2,3,4
3,5,6
4,7,8
        ''',
        id='auto_inc',
    ),
    pytest.param(
        '''\
transform Test {
    values {
        ['c'] -> ['b'] | round 1
        ['b'] -> round 0
    }
}
        ''',
        '''\
a,b,c
1,1.5,placeholder
3,4.4,placeholder
        ''',
        '''\
a,b,c
1,2.0,1.5
3,4.0,4.4
        ''',
        id='round',
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
