#!/usr/bin/env python
"""
Get a bunch of snippets from a list of authors.

Usage:
  snippeteer <authors-file> [<snippets-per-author>]
  snippeteer --help
  snippeteer --version

Options:
  -h --help     show this help message and exit
  -v --verbose  print additional information
  --version     print the version number
"""
from docopt import docopt, printable_usage
import sys
version = "0.1.0-SNAPSHOT"

usage_str = printable_usage(__doc__)


def display_error(e):
    """Display the given message as an error to the user and print the usage
    string.

    >>> display_error("Oh no!") # doctest: +ELLIPSIS
    /*/ERROR:/*/ Oh no!
    <BLANKLINE>
    Usage:
      snippeteer <authors-file> [<snippets-per-author>]
      snippeteer --help
      snippeteer --version
    """
    print(red('ERROR:', True) + ' ' + e + "\n")
    print(usage_str)


def create_repo(repo_path):
    """Do it!"""
    run('mkdir -p %s' % repo_path)
    with cd(repo_path):
        res = run('git init --bare', shell=False)
    return res


def snipeteer(arguments):
    """Main function which delegates to fabric tasks."""
    with open(arguments['<authors-file>'], 'r') as authors_file:
        authors = authors_file.readlines()


def main():
    """Runs the script."""
    # Parse options based on docstring above. If it is the first usage then...
    arguments = docopt(__doc__, argv=sys.argv[1:], version=version)
    # continue by calling this function.
    snippeteer(arguments)

if __name__ == '__main__':
    main()
