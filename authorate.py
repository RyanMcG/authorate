#!/usr/bin/env python
"""
Get a bunch of snippets from a list of authors.

Usage:
  authorate load [-v -d <path-to-db> -p <path-prefix>] <paths-file> [<snippets-per-path>]
  authorate --help
  authorate --version

Options:
  -p, --prefix <path-prefix>  a prefix to the paths given in the paths file.
  -d, --db <path-to-db>       the sqlite database to use [default: snippets.db]
  -h, --help                  show this help message and exit
  -v, --verbose               print additional information
  --version                   print the version number
"""
from docopt import docopt, printable_usage
from sqlalchemy import create_engine
import sys
import re

VERSION = "0.1.0-SNAPSHOT"

USAGE_TEXT = printable_usage(__doc__)

# Regexes
BOOK_REGEX = re.compile('^.*\.(mobi|txt|epub)$')
TITLE_REGEX = re.compile('^(.*) - .*$')

DEFAULT_SNIPPETS_COUNT = 50


def display_error(e):
    """Display the given message as an error to the user and print the usage
    string.

    >>> display_error("Oh no!") # doctest: +ELLIPSIS
    ERROR: Oh no!
    <BLANKLINE>
    Usage:
      ...
    """
    print("ERROR: {error}\n\n{usage}".format(error=e, usage=USAGE_TEXT))


def load_books(engine, author):
    pass


def authorate(arguments):
    """Main function which delegates to fabric tasks."""
    engine = create_engine('sqlite:///:memory:', echo=True)
    if arguments['load']:
        with open(arguments['<authors-file>'], 'r') as authors_file:
            authors = authors_file.readlines()
            for author in authors:
                load_books(engine, author)
    else:
        display_error("No subcommand given.")


def main():
    """Runs the script."""
    # Parse options based on docstring above. If it is the first usage then...
    arguments = docopt(__doc__, argv=sys.argv[1:], version=VERSION)
    # continue by calling this function.
    authorate(arguments)

if __name__ == '__main__':
    main()
