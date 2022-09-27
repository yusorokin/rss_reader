import argparse
from rss_reader._version import __version__

prog_name = "rss_reader"

def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Pure Python command-line RSS reader',
        prog=prog_name
        )
    parser.add_argument(
        'url',
        metavar='URL',
        action="store",
        type=str,
        help='URL to RSS feed for reading'
        )
    parser.add_argument(
        '--limit',
        dest='limit',
        action='store',
        type=int,
        nargs='?',
        default=3,
        help='limit news topics if this parameter provided'
        )
    parser.add_argument(
        '--json',
        dest='to_json',
        action='store_const',
        const=True,
        default=False,
        help='output in JSON format'
        )
    parser.add_argument(
        '--verbose',
        dest='verbose',
        action='store_const',
        const=True,
        default=False,
        help='outputs verbose status messages'
        )
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}',
        help='print version info'
        )
    return parser.parse_args(args)
