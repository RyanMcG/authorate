from sqlalchemy import (Column, Integer, String, Unicode, UnicodeText,
                        ForeignKey)
from sqlalchemy.ext.declarative import (AbstractConcreteBase, declarative_base,
                                        declared_attr)
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Model(object):
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @classmethod
    def _repr_helper(cls, **kwargs):
        return ("<{cls}".format(cls=cls.__name__) + " " +
                " ".join(["{k}=\"{v}\"".format(k=k, v=v)
                          for k, v in kwargs.items()])
                + ">")

    def __repr__(self):
        return self.__class__._repr_helper(id=self.id)


class Path(Model, Base):
    name = Column(String)
    prefix = Column(String)

    def __init__(self, name, prefix=''):
        self.name = name
        self.prefix = prefix

    def __repr__(self):
        return self.__class__._repr_helper(id=self.id, prefix=self.prefix,
                                           name=self.name)


class Book(Model, Base):
    title = Column(String)
    full_path = Column(String)
    path_id = Column(Integer, ForeignKey('path.id'), nullable=False)

    def __init__(self, title, full_path, path_id):
        self.title = title
        self.full_path = full_path
        self.path_id = path_id

    def __repr__(self):
        return self.__class__._repr_helper(id=self.id, title=self.title,
                                           full_path=self.path_id,
                                           path_id=self.path_id)


class Snippet(Model, Base):
    text = Column(UnicodeText)
    position = Column(Integer)
    book_id = Column(Integer, ForeignKey('book.id'))

    def __init__(self, text, position, book_id):
        self.text = text
        self.position = position
        self.book_id = book_id

    def __repr__(self):
        return self.__class__._repr_helper(id=self.id, book=self.book_id,
                                           position=self.position)


class WordCount(Base):
    word = Column(Unicode, primary_key=True)
    count = Column(Integer)

    __tablename__ = "word_count"

    def __init__(self, word, count):
        self.word = word
        self.count = count


def create_db(engine):
    """Create the database and tables."""
    Base.metadata.create_all(engine)


def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
