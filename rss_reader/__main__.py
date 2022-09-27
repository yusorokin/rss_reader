from rss_reader import one_shot
from rss_reader.arg_parser import parse_args
import sys

def cli():
    args = parse_args(sys.argv[1:])
    one_shot.read_rss(args.url, args.limit, args.to_json, args.verbose)

if __name__ == "__main__":
    cli()
