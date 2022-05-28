from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Float,
    Text,
    Enum,
    Numeric,
    DateTime
    

)
from sqlalchemy.orm import relationship, sessionmaker
import enum


Base = declarative_base()

class TrustLevel(enum.Enum):
    new = "new"
    basic = "basic"
    member = "member"
    regular = "regular"


class Users(Base):
    __tablename__ = "users"
    id = Column(String(50), primary_key=True)
    posts = relationship("Posts", back_populates="users")

    username = Column(String(50))
    password = Column(String(50))

    latitude = Column(Float)
    longitude = Column(Float)

    num_of_likes = Column(Integer)
    num_of_posts = Column(Integer)
    num_of_complaints = Column(Integer)

    trust_level = Column(Enum(TrustLevel))

    def __repr__(self) -> str:
        return f"<User id={self.id}>"

    @property
    def serialize(self):
        return {
            self.id: {
                "username": self.username,
                "password": self.password,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "num_of_likes": self.num_of_likes,
                "num_of_posts": self.num_of_posts,
                "num_of_complaints": self.num_of_complaints,
                "trust_level": self.trust_level.name
            }
        }

class Posts(Base):
    __tablename__ = "posts"
    users = relationship("Users", foreign_keys="Posts.author_id")

    id = Column(Integer, primary_key=True)
    author_id = Column(String(50), ForeignKey("users.id"))

    latitude = Column(Float)
    longitude = Column(Float)
    time = Column(DateTime)

    message = Column(Text)
    likes = Column(Integer)
    reports = Column(Integer)

    def __repr__(self) -> str:
        return f"<Post id={self.id} author_id={self.author_id} longitude={self.longitude} latitude={self.latitude}"

    @property
    def serialize(self):
        return {
            self.id : { 
                "author_id": self.author_id,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "message": self.message,
                "likes": self.likes,
                "complaints": self.reports
            }
        }


