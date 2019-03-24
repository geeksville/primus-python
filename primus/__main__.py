#!python

import argparse
from .client import PrimusClient
import logging


def main():
    """Perform command line primus operations"""
    parser = argparse.ArgumentParser()

    # Operations for app developers
    parser.add_argument(
        "--server", help="The server we are talking to")

    # Operations for server backend developers
    parser.add_argument("--debug", help="Show debug log message",
                        action="store_true")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    if args.server:
        client = PrimusClient()
        client.connect(args.server)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
