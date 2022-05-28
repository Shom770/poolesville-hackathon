from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from DBObjects import Base
from DBmodifier import DBModifier
from datetime import datetime

engine = create_engine(f"mysql+pymysql://root:password@db/wxweather")
session_template = sessionmaker()
session_template.configure(bind=engine)
session = scoped_session(session_template)
connection = engine.connect()

print("Creating all tables")
Base.metadata.create_all(engine)

print("Creating database object")
database = DBModifier(engine, session, connection)

print("Adding user")
database.add_user(
    username = "saraansh",
    password = "secret",
    latitude = 39.14300959208755,
    longitude = -77.28741232019671,
    num_of_likes = 0,
    num_of_posts = 0,
    num_of_complaints = 0,
    trust_level = "basic"
)

print("Adding post")
database.add_post(
    author_id = 1,
    latitude = 39.14300959208755,
    longitude = -77.28741232019671,
    time=datetime.now(),
    message= "speaking straight facts no cap no cap",
    likes = "",
    reports = "",
)

print(database.get_post(1))
database.session.commit()



