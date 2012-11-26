from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import (AbstractConcreteBase, declarative_base,
                                        declared_attr)
from sqlalchemy.orm import relationship, backref, sessionmaker

Base = declarative_base()


class PrettyBase(object):
    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @classmethod
    def _repr_helper(cls, **kwargs):
        return ("<{cls}".format(cls=cls.__name__) +
                " ".join([" {k}={v}".format(k=k, v=v) for k, v in kwargs]) +
                ">")

    def __repr__(self):
        return self.__class__._repr_helper(id=self.id)


class Author(PrettyBase, Base):
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.__class__._repr_helper(id=self.id, name=self.name)


class Book(PrettyBase, Base):
    title = Column(String)
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship('Author', backref=backref('book', order_by=id))

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return self.__class__._repr_helper(id=self.id, title=self.title,
                                           author=self.author_id)


class Snippet(PrettyBase, Base):
    text = Column(String)
    position = Column(Integer)
    book_id = Column(Integer, ForeignKey('book.id'))
    book = relationship('Book', backref=backref('book', order_by=id))

    def __init__(self, text, position):
        self.text = text
        self.position = position

    def __repr__(self):
        return self.__class__._repr_helper(id=self.id, book=self.book_id,
                                           position=self.position)


def create_db(engine):
    """Create the database and tables."""
    Base.metadata.create_all(engine)


def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
