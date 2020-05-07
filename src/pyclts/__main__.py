"""
Main command line interface to the pyclts package.
"""
import sys
from pathlib import Path
import contextlib

from cldfcatalog import Config, Catalog
from clldutils.clilib import register_subcommands, get_parser_and_subparsers, ParserError
from clldutils.loglib import Logging

from pyclts import CLTS


def main(args=None, catch_all=False, parsed_args=None):
    import pyclts.commands

    try:
        repos = Config.from_file().get_clone('clts')
    except KeyError:  # pragma: no cover
        repos = Path('.')
    parser, subparsers = get_parser_and_subparsers('clts')
    parser.add_argument(
        '--repos',
        help="clone of cldf-clts/clts",
        default=repos,
        type=Path)
    parser.add_argument(
        '--repos-version',
        help="version of repository data. Requires a git clone!",
        default=None)
    parser.add_argument(
        '--system',
        help="specify the transcription system you want to load",
        default="bipa")
    register_subcommands(subparsers, pyclts.commands)

    args = parsed_args or parser.parse_args(args=args)
    if not hasattr(args, "main"):  # pragma: no cover
        parser.print_help()
        return 1

    with contextlib.ExitStack() as stack:
        stack.enter_context(Logging(args.log, level=args.log_level))
        if args.repos_version:  # pragma: no cover
            # If a specific version of the data is to be used, we make
            # use of a Catalog as context manager:
            stack.enter_contet(Catalog(args.repos, tag=args.repos_version))
        args.repos = CLTS(args.repos)
        args.log.info('cldf-clts/clts at {0}'.format(args.repos.repos))
        try:
            return args.main(args) or 0
        except KeyboardInterrupt:  # pragma: no cover
            return 0
        except ParserError as e:  # pragma: no cover
            print(e)
            return main([args._command, '-h'])
        except Exception as e:  # pragma: no cover
            if catch_all:
                print(e)
                return 1
            raise


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main() or 0)
