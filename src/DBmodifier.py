from typing import Union, Optional, List, Literal
from DBObjects import (
    TrustLevel,
    Users,
    Posts
)
from datetime import datetime

class DBModifier():

    def __init__(self, engine, session, connection):
        print("Connecting to sql")
        self.engine = engine
        self.session = session
        self.connection = connection

    def get_user(
        self,
        user_id: str
    ) -> Optional[Users]:
        query = self.session.query(Users)
        if user_id is not None:
            query = query.filter(Users.id == user_id)
        return query.all() if query is not None else None

    def add_user(
        self,
        id: str,
        username: str,
        password: str,
        latitude: float,
        longitude: float,
        num_of_likes: int,
        num_of_posts: int,
        num_of_complaints: int,
        trust_level: str
    ):
        if not self.get_user(user_id=id):
            user_object = Users(
                id = id,
                username=username,
                password=password,
                latitude=latitude,
                longitude=longitude,
                num_of_likes=num_of_likes,
                num_of_posts=num_of_posts,
                num_of_complaints=num_of_complaints,
                trust_level = TrustLevel(trust_level)
            )
            self.session.add(user_object)
    
    def get_post(
        self,
        post_id: int,
        user_id: Optional[str]
    ) -> Optional[Posts]:
        query = self.session.query(Posts)
        if post_id is not None:
            query = query.filter(Posts.id == post_id)
        if user_id is not None:
            query = query.filter(Posts.author_id == user_id)
        return query.all() if query is not None else None
    
    def add_post(
        self,
        id: str,
        author_id: str,
        latitude: float,
        longitude: float,
        time: datetime,
        message: str,
        likes: int,
        reports: int
    ):
        if not self.get_post(post_id=id, user_id=None):
            post_object = Posts(
                id=id,
                author_id=author_id,
                latitude=latitude,
                longitude=longitude,
                time=time,
                message=message,
                likes=likes,
                reports=reports
            )
            self.session.add(post_object)
    
            

