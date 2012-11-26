from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import (AbstractConcreteBase, declarative_base,
                                        declared_attr)
from sqlalchemy.orm import relationship, backref, sessionmaker

Base = declarative_base()


class Model(object):
    __mapper_args__ = {'always_refresh': True}
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

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.__class__._repr_helper(id=self.id, name=self.name)


class Book(Model, Base):
    title = Column(String)
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship('Author', backref=backref('book', order_by=id))

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return self.__class__._repr_helper(id=self.id, title=self.title,
                                           author=self.author_id)


class Snippet(Model, Base):
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
