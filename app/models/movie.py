from sqlalchemy import BigInteger, Column, Float, Integer, String

from app.database import Base


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    genres = Column(String, nullable=False)


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    movie_id = Column(Integer, nullable=False, index=True)
    rating = Column(Float, nullable=False)
    timestamp = Column(BigInteger, nullable=False)
