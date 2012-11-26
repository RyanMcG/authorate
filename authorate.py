#!/usr/bin/env python
"""
Get a bunch of snippets from a list of authors.

Usage:
  authorate load [-v --one -d <path-to-db> -p <path-prefix>] <paths-file> [<snippets-per-path>]
  authorate --help
  authorate --version

Options:
  -p, --prefix <path-prefix>  a prefix to the paths given in the paths file.
  -d, --db <path-to-db>       the sqlite database to use [default: snippets.db]
  -h, --help                  show this help message and exit
  -v, --verbose               print additional information
  --version                   print the version number
  --one                       Use only one thread.
"""
from docopt import docopt, printable_usage
from sqlalchemy import create_engine
from model import create_db, get_session, Path, Book, Snippet
from multiprocessing.pool import Pool
from itertools import chain
from tempfile import NamedTemporaryFile
import sys
import os
import re
import subprocess
import random

VERSION = "0.1.0-SNAPSHOT"

USAGE_TEXT = printable_usage(__doc__)

# Regexes
BOOK_REGEX = re.compile('^.*\.(mobi|txt|epub)$')
TITLE_REGEX = re.compile('^(.*) - .*$')

DEFAULT_SNIPPETS_COUNT = 50
MIN_SNIPPET_SIZE = 70


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


def load_snippets_from_txt_file(txt_file, snippet_count):
    """Load snippet_count snippets from the given text file."""
    pass

def load_snippets(book_path_and_snippet_count):
    """Load snippet count snippets from the given book."""
    book_path, snippet_count = book_path_and_snippet_count
    with NamedTemporaryFile(suffix='.txt') as txt_file:
        args_list = ['ebook-convert', book_path, txt_file.name]
        with open(os.devnull, 'w') as stdout:
            return_value = subprocess.call(args_list, stdout=stdout)
        if return_value == 0:
            return load_snippets_from_txt_file(txt_file, snippet_count)
        else:
            display_error("Failed to execute the following command: {cmd}".format(
                cmd=" ".join(args_list)))
            return []


def num_snippets_per_book(books, snippet_count):
    """A generator that returns tupples of paths and the snippet counts."""
    num_books = len(books)
    snippets_per_book = snippet_count / num_books
    extra_book_max_index = snippet_count % num_books

    for i, book in enumerate(books):
        # Determine the number of snippets load for this book.
        num_snippets = snippets_per_book
        if i < extra_book_max_index:
            num_snippets += 1
        yield (book.full_path, num_snippets)


def load_books(books, snippet_count, multi_thread=True):
    """Return snippet_count snippets from the given books."""
    random.shuffle(books)
    generator = num_snippets_per_book(books, snippet_count)
    if multi_thread:
        pool = Pool()
        mapper = pool.map
    else:
        mapper = map
    return chain.from_iterable(mapper(load_snippets, generator))


def load_path(session, path, snippet_count=DEFAULT_SNIPPETS_COUNT, prefix='',
              verbose=False, multi_thread=False):
    """For the given path create Path, Book and Snippet entries.

    Each entry is put into the databse via the given session. Each run of load_books should create"""
    if verbose:
        print("Loading path: {path}".format(path=path))

    # Create an instance of the given path in the database.
    path_inst = Path(path, prefix)
    session.add(path_inst)
    session.commit()

    books = []
    full_path = os.path.join(prefix, path)
    if not os.path.exists(full_path):
        display_error("The given path does not exist: {path}".format(
            path=full_path))
        return False

    for root, dirs, files in os.walk(full_path):
        book_paths = filter(BOOK_REGEX.match, files)
        if len(book_paths) > 0:
            # Get the title and full path for the first book in this directory.
            book_name = book_paths[0]
            title = filename_to_title(book_name)
            full_book_path = os.path.join(root, book_name)

            # Create an instance of the book and add it to the databse.
            book_inst = Book(title, full_book_path, path_inst.id)
            session.add(book_inst)
            books.append(book_inst)

    # Commit all of the books
    session.commit()

    # Load snippets from given books and commit them.
    session.add_all(load_books(books, snippet_count, multi_thread))
    session.commit()
    return True


def authorate(arguments):
    """Main function which delegates to fabric tasks."""
    engine = create_engine('sqlite:///' + arguments['--db'])
    create_db(engine)
    session = get_session(engine)
    verbose = arguments['--verbose']
    multi_thread = not arguments['--one']

    # Assume successful return value
    ret = 0
    if arguments['load']:
        prefix = arguments['--prefix']
        if os.path.exists(prefix):
            # Determine how many snippets to get per path.
            snippets_count = arguments['<snippets-per-path>']
            if not snippets_count:
                snippets_count = DEFAULT_SNIPPETS_COUNT

            with open(arguments['<paths-file>'], 'r') as paths_file:
                paths = paths_file.readlines()
                for path in paths:
                    if not load_path(session, path.rstrip(), prefix=prefix,
                                     multi_thread=multi_thread):
                        ret = 3
        else:
            display_error("The given prefix does not exist: {path}".format(
                path=prefix))
            ret = 2
    else:
        display_error("No subcommand given.")
        ret = 1
    return ret


def main():
    """Runs the script."""
    # Parse options based on docstring above. If it is the first usage then...
    arguments = docopt(__doc__, argv=sys.argv[1:], version=VERSION)
    # continue by calling this function.
    return authorate(arguments)

if __name__ == '__main__':
    sys.exit(main())
