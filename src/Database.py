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




