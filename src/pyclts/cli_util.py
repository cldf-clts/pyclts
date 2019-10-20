import tabulate

from clldutils import markup


def add_format(parser, default='pipe'):
    parser.add_argument(
        "--format",
        default=default,
        choices=tabulate.tabulate_formats,
        help="Format of tabular output.")


class Table(markup.Table):
    def __init__(self, args, *cols):
        super().__init__(*cols)
        self._fmt = args.format

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if len(self):
            print(self.render(tablefmt=self._fmt, condensed=False, floatfmt='.2f'))
