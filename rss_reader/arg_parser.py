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
        type=str,
        nargs="?",
        default=None,
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
        help='prints version info'
        )
    parser.add_argument(
        '--date',
        dest='date',
        action='store',
        type=str,
        nargs='?',
        default=None,
        help='get cached feed for the given date'
        )
    parsed_args = parser.parse_args(args)
    if (parsed_args.date is None and parsed_args.url is None):
        parser.error("Mandatory positional argument 'URL' is missing")

    return parsed_args
