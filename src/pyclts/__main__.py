"""
Main command line interface to the pyclts package.
"""
import sys
from pathlib import Path

from clldutils.clilib import register_subcommands, get_parser_and_subparsers, ParserError
from clldutils.loglib import Logging

from pyclts import CLTS


def main(args=None, catch_all=False, parsed_args=None):
    import pyclts.commands

    parser, subparsers = get_parser_and_subparsers('clts')
    parser.add_argument(
        '--repos', help="clone of cldf-clts/clts", default=Path('.'), type=Path)
    parser.add_argument(
        '--system',
        help="specify the transcription system you want to load",
        default="bipa")
    register_subcommands(subparsers, pyclts.commands)

    args = parsed_args or parser.parse_args(args=args)
    if not hasattr(args, "main"):
        parser.print_help()
        return 1

    args.repos = CLTS(args.repos)
    with Logging(args.log, level=args.log_level):
        try:
            return args.main(args) or 0
        except KeyboardInterrupt:  # pragma: no cover
            return 0
        except ParserError as e:
            print(e)
            return main([args._command, '-h'])
        except Exception as e:
            if catch_all:  # pragma: no cover
                print(e)
                return 1
            raise


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main() or 0)
