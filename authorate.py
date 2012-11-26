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
from model import create_db, get_session, Path
import sys
import os
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


def filename_to_title(filename):
    """For the given filename or path return the title of the book.

    Typically, a filename is something like "TITLE - AUTHOR.EXTENSION". This
    function assumes that pattern holds and extracts the TITLE portion.

    >>> filename_to_title('David Copperfield - Charles Dickens.txt')
    'David Copperfield'
    >>> filename_to_title('Ugly - Title - Bad-Guy.mobi')
    'Ugly - Title'
    """
    name, _ = os.path.splitext(os.path.basename(filename))
    return TITLE_REGEX.match(name).groups()[0]


def load_books(session, path, snippet_count=DEFAULT_SNIPPETS_COUNT, prefix='', verbose=False):
    """For the given path create Path, Book and Snippet entries.

    Each entry is put into the databse via the given session. Each run of load_books should create"""
    if verbose:
        print("Loading path: {path}".format(path=path))

    # Create an instance of the given path in the database.
    path_inst = Path(path, prefix)
    session.add(path_inst)
    session.commit()

    book_paths = []
    full_path = os.path.join(prefix, path)
    for root, dirs, files in os.walk(full_path):
        books = filter(BOOK_REGEX.match, files)
        if len(books) > 0:
            book_name = books[0]
            title = filename_to_title(book_name)
            book_paths.append(os.path.join(root, book_name))


def authorate(arguments):
    """Main function which delegates to fabric tasks."""
    engine = create_engine('sqlite:///' + arguments['--db'])
    create_db(engine)
    session = get_session(engine)
    verbose = arguments['--verbose']

    if arguments['load']:
        prefix = arguments['--prefix']

        # Determine how many snippets to get per path.
        snippets_count = arguments['<snippets-per-path>']
        if not snippets_count:
            snippets_count = DEFAULT_SNIPPETS_COUNT

        with open(arguments['<paths-file>'], 'r') as paths_file:
            paths = paths_file.readlines()
            for path in paths:
                load_books(session, path.rstrip(), prefix=prefix)
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
