from flask_cors import CORS
from flask import Flask, render_template, jsonify
from flask.globals import request
from DBmodifier import DBModifier
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy import create_engine
from waitress import serve
from datetime import datetime
import hashlib

app = Flask(__name__)
CORS(app, CORS_ORIGINS="*") #we will not get api bullied >:(
app.config['CORS_HEADERS'] = 'Content-Type'


def refresh_db(db=None):
    engine = create_engine(f"mysql+pymysql://root:password@db/wxweather")
    session_template = sessionmaker()
    session_template.configure(bind=engine)
    session = scoped_session(session_template)
    connection = engine.connect()

    db.engine = engine
    db.session = session
    db.connection = connection
    return db

engine = create_engine(f"mysql+pymysql://root:password@db/wxweather")
session_template = sessionmaker()
session_template.configure(bind=engine)
session = scoped_session(session_template)
connection = engine.connect()
db = DBModifier(engine, session, connection)

@app.route("/userinfo/<userid>", methods=["GET"])
def get_user_info(userid):
    return jsonify(
        [user.serialize for user in refresh_db(db).get_user(user_id=userid)]
    )

@app.route("/logintosite", methods=["POST"])
def login():
    data = request.args
    userdata = db.id_and_pass(data["username"])
    passwordhash = hashlib.md5(data["password"].encode("utf-8")).hexdigest()
    if passwordhash == userdata[1]:
        return userdata[0]
    else:
        return "invalid"

@app.route("/adduser", methods=["POST"])
def add_user():
    #commit data before adding idk why there would be data to commit dude i hate sql
    db.session.commit()
    data = request.args

    db.add_user(
        username = data["username"],
        password = hashlib.md5(data["password"].encode("utf-8")).hexdigest(),
        latitude = float(data["latitude"]),
        longitude = float(data["longitude"]),
        num_of_likes = int(data["num_of_likes"]),
        num_of_posts = int(data["num_of_posts"]),
        num_of_complaints = int(data["num_of_complaints"]),
        trust_level = data["trust_level"]
    )

    db.session.commit()
    return "User added!"
    
@app.route("/modifyuser", methods=["POST"])
def modify_user():
    db.session.commit()
    data = request.args
    
    db.modify_user(
        id = data["id"],
        username = data["username"] if data["username"] is not None else None,
        password = data["password"] if data["password"] is not None else None,
        latitude = float(data["latitude"]) if data["latitude"] is not None else None,
        longitude = float(data["longitude"]) if data["longitude"] is not None else None,
        num_of_likes = int(data["num_of_likes"]) if data["num_of_likes"] is not None else None, 
        num_of_posts = int(data["num_of_posts"]) if data["num_of_posts"] is not None else None,
        num_of_complaints = int(data["num_of_complaints"]) if data["num_of_complaints"] is not None else None,
        trust_level = data["trust_level"] if data["trust_level"] is not None else None,
    )

    return "User info changed!"

@app.route("/postinfobypostid/<postid>", methods = ["GET"])
def get_post_by_postid(postid):
    return jsonify(
        [post.serialize for post in refresh_db(db).get_post(post_id=postid)]
    )

@app.route("/postinfobyuid/<uid>", methods = ["GET"])
def get_post_by_uid(uid):
    return jsonify(
        [post.serialize for post in refresh_db(db).get_post(user_id=uid)]
    )

@app.route("/add_post", methods = ["POST"])
def add_post():
    db.session.commit()
    data = request.args

    db.add_post(
        author_id = data["author_id"],
        latitude=data["latitude"],
        longitude=data["longitude"],
        time = datetime.now(),
        message = data["message"],
        likes = data["likes"],
        reports = data["reports"]
    )

    db.modify_user(
        id = data["author_id"],
        num_of_posts = db.get_total_user_posts(data["author_id"]) + 1
    )

    db.session.commit()
    return "Added post!"

@app.route("/modify_post", methods = ["POST"])
def modify_post():
    """
    int: post_id
    int: modifier_user_id
    boolean: modified_likes 
    boolean: modified_reports
    """

    db.session.commit()

    data = request.args
    modifier = str(data["modifier_user_id"])
    
    #booleans
    modified_likes = data["modified_likes"]
    modified_reports = data["modified_reports"]

    trust_level = ["new", "basic", "member", "regular"]

    new_likes = 0
    new_reports = 0
    if modified_likes: #check if it has been liked
        post_likes = db.get_likes_of_post(post_id = data["post_id"])
        if modifier in post_likes:
            post_likes.pop(post_likes.index(modifier))
            new_likes = -1
        else:
            post_likes.append(modifier)
            new_likes = 1

    if modified_reports: #check if it has been reported
        post_reports = db.get_reports_of_post(post_id = data["post_id"])
        if modifier in post_reports:
            post_reports.pop(post_reports.index(modifier))
            new_reports = -1
        else:
            post_reports.append(modifier)
            new_reports = 1
    
    db.modify_post(
        id = data["post_id"],
        likes = ";".join(post_likes) if modified_likes else None,
        reports = ";".join(post_reports) if modified_reports else None 
        )
    
    user_id = db.get_post_owner(post_id=data["post_id"])
    db.modify_user(
        id = user_id,
        num_of_likes = db.get_total_user_likes(user_id) + new_likes,
        num_of_complaints= db.get_total_user_reports(user_id) + new_reports,
        trust_level = trust_level[int((db.get_total_user_likes(user_id) + new_likes) / 10)]
    )
    
    db.session.commit()
    return "Modified Post!"    


if __name__ == "__main__":
    serve(
        app,
        host="0.0.0.0",
        port="8001"
    )



