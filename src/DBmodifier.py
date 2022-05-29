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
        user_id: int
    ) -> Optional[Users]:
        query = self.session.query(Users)
        if user_id is not None:
            query = query.filter(Users.id == user_id)
        return query.all() if query is not None else None
    
    def get_user_from_username(
        self,
        username: str
    ) -> Optional[Users]:
        query = self.session.query(Users)
        if username is not None:
            query = query.filter(Users.username == username)
        return query.all() if query is not None else None

    def add_user(
        self,
        username: str,
        password: str,
        latitude: float,
        longitude: float,
        num_of_likes: int,
        num_of_posts: int,
        num_of_complaints: int,
        trust_level: str
    ):
        user_object = Users(
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
        post_id: int = None,
        user_id: Optional[str] = None
    ) -> Optional[List[Posts]]:
        query = self.session.query(Posts)

        if post_id is not None:
            query = query.filter(Posts.id == post_id)
        
        if user_id is not None:
            query = query.filter(Posts.author_id == user_id)
        
        return query.all() if query is not None else None
    
    def add_post(
        self,
        author_id: str,
        latitude: float,
        longitude: float,
        time: datetime,
        message: str,
        likes: str,
        reports: str
    ):
        if not self.get_post(post_id=id, user_id=None):
            post_object = Posts(
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
        id: int,
        username: str = None,
        password: str = None,
        latitude: float = None,
        longitude: float = None,
        num_of_likes: int = None,
        num_of_posts: int = None,
        num_of_complaints: int = None,
        trust_level: str = None
    ):
        user = self.get_user(user_id=id)[0]

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
        author_id: str = None,
        latitude: float = None,
        longitude: float = None,
        time: datetime = None,
        message: str = None,
        likes: str = None,
        reports: str = None
    ):
        post = self.get_post(post_id=id)[0]
        
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
    
    def get_likes_of_post(
        self,
        post_id: int
    ) -> List[str]:
        post = self.get_post(post_id=post_id)[0]
        return str(post.likes).split(";")
    
    def get_reports_of_post(
        self,
        post_id: int
    ) -> List[str]:
        post = self.get_post(post_id=post_id)[0]
        return str(post.likes).split(";")
    
    def get_post_owner(
        self,
        post_id: int
    ) -> int:
        post = self.get_post(post_id=post_id)[0]
        return post.author_id
    
    def get_total_user_likes(
        self,
        user_id: int
    ) -> int:
        user = self.get_user(user_id = user_id)[0]
        return user.num_of_likes
    
    def get_total_user_reports(
        self,
        user_id: int
    ) -> int:
        user = self.get_user(user_id = user_id)[0]
        return user.num_of_complaints
    
    def get_total_user_posts(
        self,
        user_id: int
    ) -> int:
        user = self.get_user(user_id = user_id)[0]
        return user.num_of_posts
    
    def id_and_pass(
        self,
        username: str
    ) -> tuple:
        user = self.get_user_from_username(username=username)[0]
        return (user.id, user.password)
    
    def get_coordinates(
        self,
        client_user_id: str
    ) -> tuple:
        user = self.get_user(user_id=int(client_user_id[2:]))[0]
        return (user.latitude, user.longitude)
        
    def get_trust_level(
        self,
        user_id: int
    ) -> str:
        user = self.get_user(user_id=user_id)[0]
        return user.trust_level.name
        








        
    
            

