class Loader(object):
    # Regexes
    BOOK_REGEX = re.compile('^.*\.(mobi|txt|epub)$')
    TITLE_REGEX = re.compile('^(.*) - .*$')

    DEFAULT_SNIPPETS_COUNT = 50
    MIN_SNIPPET_SIZE = 70

    def __init__(self, arguments):
        self.__parse_args(arguments)
        self._pool = Pool(cpu_count() if self.multi_thread else 1)

    def __parse_args(self.arguments):
        self.engine = create_engine('sqlite:///' + arguments['--db'])
        self.verbose = arguments['--verbose']
        self.multi_thread = not arguments['--one']
        self.prefix = arguments['--prefix']

        if os.path.exists(prefix):
            # Determine how many snippets to get per path.
            self.snippets_count = arguments['<snippets-per-path>']
            if not self.snippets_count:
                self.snippets_count = DEFAULT_SNIPPETS_COUNT
            self.paths_filename = arguments['<paths-file>']
        else:
            raise InvalidArgumentError

    def start(self):
        ret = 0
        with open(self.paths_filename, 'r') as paths_file:
            paths = paths_file.readlines()
            for path in paths:
                res = self._load_path(self._pool, path.rstrip(), prefix=prefix, multi_thread=multi_thread)
                if not res:
                    ret = 3
        # Join the pool
        pool.close()
        pool.join()
        return ret
