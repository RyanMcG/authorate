"""
Get a bunch of snippets from a list of authors.

Usage:
  authorate load [-v --one -d <path-to-db> -p <path-prefix>] <paths-file> [<snippets-per-path>]
  authorate process [-v -d <path-to-db>]
  authorate classify ([-]|<snippet-file>)
  authorate --help
  authorate --version

Arguments:
  <paths-file>                A file containing paths separated by newlines to
                              load snippets from.

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
from multiprocessing import cpu_count
from multiprocessing.pool import Pool
from itertools import chain
from tempfile import NamedTemporaryFile
from codecs import EncodedFile
import fileinput
import sys
import os
import re
import subprocess
import random

VERSION = "0.1.0-SNAPSHOT"
VERBOSE = False

USAGE_TEXT = printable_usage(__doc__)

# Regexes
BOOK_REGEX = re.compile('^.*\.(mobi|txt|epub)$')
TITLE_REGEX = re.compile('^(.*) - .*$')

DEFAULT_SNIPPETS_COUNT = 50
MIN_SNIPPET_SIZE = 70


engine = None


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


def guarded_readline(encoded_file):
    """A wrapper around readline to catch UnicodeDecodeErrors without
    breaking."""
    try:
        line = encoded_file.readline()
    except UnicodeDecodeError as e:
        line = ''
        print("ERROR: Coult not decode line: \"{line}\"".format(
            line=repr(line)))
    finally:
        return line


def load_snippets_from_txt_file(txt_file, snippet_count, book_id):
    """Load snippet_count snippets from the given text file."""
    size = os.path.getsize(txt_file.name)

    snippets = set()
    enc_file = EncodedFile(txt_file.file, 'utf-8', errors='ignore')
    while len(snippets) < snippet_count:
        starting_byte = random.randint(size / 10, 9 * size / 10)
        # Ignore the first line read since the cursor my start in the middle.
        enc_file.seek(starting_byte)
        line = guarded_readline(enc_file)

        pos = enc_file.tell()
        for i in range(2):
            line = guarded_readline(enc_file)
            if len(line) >= MIN_SNIPPET_SIZE:
                line = unicode(line, encoding='utf-8', errors='ignore')
                if VERBOSE:
                    print("{0} : {1}".format(txt_file.name, pos))
                snippets.add((line.strip(), pos, book_id))
                break
            pos = enc_file.tell()

    return snippets


def load_snippets(book_id, book_path, snippet_count):
    """Load snippet count snippets from the given book."""
    with NamedTemporaryFile(suffix='.txt') as txt_file:
        args_list = ['ebook-convert', book_path, txt_file.name]
        with open(os.devnull, 'w') as stdout:
            return_value = subprocess.call(args_list, stdout=stdout)
        if return_value == 0:
            return load_snippets_from_txt_file(txt_file, snippet_count,
                                               book_id)
        else:
            display_error("Failed to execute the following command: {cmd}".format(
                cmd=" ".join(args_list)))
            return []


def num_snippets_per_book(books, snippet_count):
    """A generator that returns tupples of paths and the snippet counts."""
    num_books = len(books)
    snippets_per_book = snippet_count / num_books
    extra_book_max_index = snippet_count % num_books
    # Sort books by size descending so the largest book is converted first.
    books.sort(key=lambda book: os.path.getsize(book.full_path), reverse=True)
    for i, book in enumerate(books):
        # Determine the number of snippets load for this book.
        num_snippets = snippets_per_book
        if i < extra_book_max_index:
            num_snippets += 1
        yield (book.id, book.full_path, num_snippets)


def snippet_callback(snippets):
    session = get_session(engine)
    session.add_all(Snippet(*snip) for snip in snippets)
    session.commit()


def load_books(pool, books, snippet_count, multi_thread=True):
    """Return snippet_count snippets from the given books."""
    for item in num_snippets_per_book(books, snippet_count):
        pool.apply_async(load_snippets, item, callback=snippet_callback)
        if VERBOSE:
            print("\tBook enqueued: {book}".format(book=item[1]))


def load_path(pool, path, snippet_count=DEFAULT_SNIPPETS_COUNT, prefix='',
              multi_thread=True):
    """For the given path create Path, Book and Snippet entries.

    Each entry is put into the databse via the given session. Each run of load_books should create"""
    if VERBOSE:
        print("Loading path: {path}".format(path=path))

    # Create an instance of the given path in the database.
    path_inst = Path(path, prefix)
    session = get_session(engine)
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
    load_books(pool, books, snippet_count, multi_thread)
    return True


def authorate(arguments):
    """Main function which delegates to fabric tasks."""
    global engine
    engine = create_engine('sqlite:///' + arguments['--db'])
    create_db(engine)

    global VERBOSE
    VERBOSE = arguments['--verbose']
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

            pool = Pool(cpu_count() if multi_thread else 1)
            with open(arguments['<paths-file>'], 'r') as paths_file:
                paths = paths_file.readlines()
                for path in paths:
                    res = load_path(pool, path.rstrip(), prefix=prefix, multi_thread=multi_thread)
                    if not res:
                        ret = 3
            # Join the pool
            pool.close()
            pool.join()
        else:
            display_error("The given prefix does not exist: {path}".format(
                path=prefix))
            ret = 2
    elif arguments['process']:
        from authorate.text_feature import text_to_vector
        from authorate.classify import classifier_types
        snippets = []  # Get from the database
        data = [text_to_vector(snip.text) for snip in snippets]
        targets = [snip.path_id for snip in snippets]
        for Cls in classifier_types:
            classifier = Cls(data, targets)
            classifier.save()

    elif arguments['classify']:
        from authorate.classify import classify_all

        snip_file = arguments['<snippet-file>']
        input_files = [snip_file if snip_file else '-']
        classify_all(engine, " ".join([line.rstrip() for line in
                                       fileinput.input(input_files)]))
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
