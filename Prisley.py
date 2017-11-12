from flask import *
from bson.json_util import dumps
import pymysql
import helper
import os

app = Flask(__name__)
app.secret_key = "qwre953heqirhv3,;qgbh4549s/;,"
db = pymysql.connect(host="localhost",
                     user="root",
                     password="root",
                     db="soccerSite",
                     cursorclass=pymysql.cursors.DictCursor)

cursor = db.cursor()
ROOT_DIR = os.path.dirname(__file__)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        users = helper.query("SELECT * FROM users WHERE (username='{0}' AND password='{1}') OR (email='{0}' AND password='{1}');".
                             format(request.form["username"], request.form["password"]), cursor)
        user_list = list(users)
        user_teams = list(helper.query("SELECT * FROM user_team_rela WHERE(user_id = {0});".format(user_list[0]["user_id"]), cursor))
        user_teams = [team["team_id"] for team in user_teams]
        if user_list:
            session["user_id"] = user_list[0]["user_id"]
            session["user_avatar"] = user_list[0]["avatar"]
            session["username"] = user_list[0]["username"]
            session["user_teams"] = user_teams
            return redirect(url_for("home"))
        return redirect(url_for("login"))


@app.route('/signup')
def sign_up():
    return render_template("signup.html")


@app.route('/')
@app.route("/home", methods = ["GET", "POST"])
def home():
    if request.method == "GET":
        if "user_id" in session:
            team_logo_links = []
            for team_id in session["user_teams"]:
                team_logo_links.append(list(helper.query("SELECT * FROM teams WHERE (team_id={0});".format((team_id)), cursor))[0]["team_logo"])
            return render_template("home.html", user_id = session["user_id"],
                                                user_avatar = session["user_avatar"],
                                                username = session["username"],
                                                user_teams = session["user_teams"],
                                                team_logos = team_logo_links)
        else:
            return redirect(url_for("login"))
    elif request.method == "POST":
        if request.form["actionType"] == "pin":
            if request.form["action"] == "+":
                helper.update(" INSERT INTO pin_unpin (user_id, field_id) VALUES ({0}, {1});".format(session["user_id"], request.form["field_id"]), cursor, db)
            else:
                helper.update("DELETE FROM pin_unpin WHERE(user_id={0} AND field_id={1});".format(session["user_id"], request.form["field_id"]), cursor, db)
        elif request.form["actionType"] == "join":
            if request.form["action"] == "+":
                helper.update(" INSERT INTO request_to_join (user_id, match_id) VALUES ({0}, {1});".format(session["user_id"], request.form["match_id"]), cursor, db)
            else:
                helper.update("DELETE FROM request_to_join WHERE(user_id={0} AND match_id={1});".format(session["user_id"], request.form["match_id"]), cursor, db)
    return "Hello world"


@app.route("/return_matchups", methods=["POST"])
def return_appointment():
    if request.method == "POST":
        field = list(helper.query("SELECT * FROM fields WHERE (field_id={0});".format(request.form["field_id"]), cursor))[0]
        is_pinned = list(helper.query("SELECT * FROM pin_unpin WHERE (user_id={0} AND field_id={1});".format(session["user_id"], request.form["field_id"]), cursor))
        match_ups = helper.query("SELECT * FROM matchups WHERE (field_id={0});".format(request.form["field_id"]), cursor)
        match_up_list = []
        field_images = os.listdir(os.path.join(ROOT_DIR, "static/images/stadiums", request.form["field_id"]))
        for match_up in match_ups:
            user = list(helper.query("SELECT * FROM users WHERE (user_id)={0};".format(match_up["challenger_id"]), cursor))[0]
            team = list(helper.query("SELECT * FROM teams WHERE (team_id)={0}".format(match_up["team_id"]), cursor))[0]
            request_to_joins = helper.query("SELECT * FROM request_to_join WHERE (match_id)={0};".format(match_up["match_id"]), cursor)
            requester_id_list = [requester["user_id"] for requester in request_to_joins]
            match_up_list.append({"username": user["username"],
                                  "avatar": user["avatar"],
                                  "team": team["team_name"],
                                  "time": match_up["time"],
                                  "comment": match_up["comment"],
                                  "match_id": match_up["match_id"],
                                  "is_joinned": True if session["user_id"] in requester_id_list else False,
                                  "request_num": len(requester_id_list)
                                })
        return dumps({"field_name": field["field_name"],
                      "field_image": "/static/images/stadiums/" + request.form["field_id"] + "/" + field_images[0],
                      "open_time": field["open_time"],
                      "close_time": field["close_time"],
                      "is_pinned": True if is_pinned else False,
                      "match_ups": match_up_list
                      })


@app.route("/return_fields", methods=["POST"])
def return_fields():
    if request.method == "POST":
        fields = helper.query("SELECT * FROM fields;", cursor)
        field_info = [{"field_id": field["field_id"], "lat": float(field["latitude"]), "lng": float(field["longtitude"])} for field in fields]
        return dumps(field_info)


@app.route("/return_teams", methods = ["POST"])
def return_teams():
    if request.method == "POST":
        user_teams = list(helper.query("SELECT * FROM user_team_rela WHERE(user_id = {0});".format(session["user_id"]), cursor))


# where field owners can set their price range, update their description etc
@app.route("/fieldowners")
def field_owner():
    return "Hello field owners"


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("user_avatar", None)
    session.pop("username", None)


if __name__ == '__main__':
    app.run()
