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
        user_id: Optional[str] = None
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
    
    def modify_user(
        self,
        id: str,
        username: str = None,
        password: str = None,
        latitude: float = None,
        longitude: float = None,
        num_of_likes: int = None,
        num_of_posts: int = None,
        num_of_complaints: int = None,
        trust_level: str = None
    ):
        user = self.get_user(user_id=id)

        if username is not None:
            user.username = username
        
        if password is not None:
            user.password = password
        
        if latitude is not None:
            user.latitude = latitude
        
        if longitude is not None:
            user.longitude = longitude
        
        if num_of_likes is not None:
            user.num_of_likes = num_of_likes
        
        if num_of_posts is not None:
            user.num_of_posts = num_of_posts
        
        if num_of_complaints is not None:
            user.num_of_complaints = num_of_complaints
        
        if trust_level is not None:
            user.trust_level = TrustLevel(trust_level)

        self.session.commit()
    
    def modify_post(
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
        post = self.get_post(post_id=id)
        
        if author_id is not None:
            post.author_id = author_id
        
        if latitude is not None:
            post.latitude = latitude
        
        if longitude is not None:
            post.longitude = longitude
        
        if time is not None:
            post.time = time
        
        if message is not None:
            post.message = message
        
        if likes is not None:
            post.likes = likes
        
        if reports is not None:
            post.reports = reports
        
        self.session.commit()


        
    
            

