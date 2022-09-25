import one_shot
from arg_parser import parse_args
import sys

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    one_shot.read_rss(args.url, args.limit, args.to_json, args.verbose)
