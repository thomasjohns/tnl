import argparse
import os

import pandas as pd  # type: ignore

from tnl.lexer import Lexer
from tnl.parser import Parser
from tnl.ast_printer import print_module_ast
from tnl.code_printer import print_module_code
from tnl.vm import transform


def exec_cli() -> int:
    argparser = argparse.ArgumentParser(
        description='TNL - Table Normalization Language.'
    )

    argparser.add_argument(
        'source_file',
        type=str,
        help='A tnl source file.',
    )

    argparser.add_argument(
        'data_file',
        type=str,
        help='A data file containing data to transform.',
    )

    stage_group = argparser.add_mutually_exclusive_group(required=False)

    stage_group.add_argument(
        '--print-tokens',
        action='store_const',
        const=True
    )
    stage_group.add_argument('--print-ast', action='store_const', const=True)
    stage_group.add_argument('--print-code', action='store_const', const=True)
    stage_group.add_argument('--check', action='store_const', const=True)
    stage_group.add_argument('--interpret', action='store_const', const=True)
    stage_group.add_argument('--compile', dest='target', default='pandas')

    args = argparser.parse_args()

    if not os.path.exists(args.source_file):
        print(f'Can\'t find source_file {args.source_file}.')
        return 1

    with open(args.source_file, 'r') as fp:
        src = fp.read()

    lexer = Lexer(src, args.source_file)
    tokens = lexer.lex()

    if args.print_tokens:
        for token in tokens:
            print(token)
        return 0

    parser = Parser(tokens, args.source_file)
    ast = parser.parse()

    if args.print_ast:
        print_module_ast(ast)
        return 0

    if args.print_code:
        print_module_code(ast)
        return 0

    if args.check:
        # TODO: implement static analysis
        print('`check` does nothing right now.')
        return 0

    if not os.path.exists(args.data_file):
        print(f'Can\'t find data_file {args.data_file}.')
        return 1

    # TODO: don't necessarily assume csv in the future
    data = pd.read_csv(args.data_file)

    if args.interpret:
        transformed_data = transform(ast, data)
        print(transformed_data.to_csv(index=False))
        return 0

    # TODO: implement compile to pandas code
    # if args.compile == 'pandas'  ...
    print(args.target)
    print('`compile` does nothing right now.')

    return 0
