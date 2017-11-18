from flask import *
from bson.json_util import dumps
import pymysql
import helper
import os
import random

app = Flask(__name__)
app.secret_key = "qwre953heqirhv3,;qgbh4549s/;,"
db = pymysql.connect(host="localhost",
                     user="root",
                     password="root",
                     db="soccerSite",
                     cursorclass=pymysql.cursors.DictCursor)

cursor = db.cursor()
ROOT_DIR = os.path.dirname(__file__)


@app.route("/")
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        user = list(helper.query("SELECT * FROM users WHERE (username='{0}' AND password='{1}') OR (email='{0}' AND password='{1}');".
                             format(request.form["username"], request.form["password"]), cursor))
        if user:
            session["user_id"] = user[0]["user_id"]
            fields = list(helper.query("SELECT * FROM pin_unpin WHERE (user_id={0});".format(session["user_id"]), cursor))
            if len(fields) > 0:
                field_id = random.choice(fields)["field_id"]
            else:
                fields = list(helper.query("SELECT * FROM fields;", cursor))
                field_id = random.choice(fields)["field_id"]
            return redirect(url_for("home", field_id=field_id))
        return redirect(url_for("login"))


@app.route('/signup')
def sign_up():
    return render_template("signup.html")


@app.route("/<username>", methods = ["GET", "POST"])
def profile(username):
    if request.method == "GET":
        return render_template("profile.html", user_id = session["user_id"],
                                               username = session["username"],
                                               user_avatar = session["user_avatar"],
                                               user_teams = session["user_teams"]
                               )


@app.route("/home/<int:field_id>", methods = ["GET", "POST"])
def home(field_id):
    if request.method == "GET":
        if "user_id" in session:
            user = list(helper.query("SELECT * FROM users WHERE (user_id = {0})".format(session["user_id"]), cursor))[0]
            session["user_avatar"] = user["avatar"]
            session["username"] = user["username"]
            user_team_ids = list(helper.query("SELECT * FROM user_team_rela WHERE(user_id = {0});".format(session["user_id"]), cursor))
            user_team_ids = [team["team_id"] for team in user_team_ids]
            user_teams = [list(helper.query("SELECT * FROM teams WHERE (team_id={0});".format((team_id)), cursor))[0] for team_id in user_team_ids]
            session["user_teams"] = [{"team_id" : user_team["team_id"],
                                      "team_name": user_team["team_name"],
                                      "team_logo": user_team["team_logo"]} for user_team in user_teams]
            field = list(helper.query("SELECT * FROM fields WHERE (field_id={0});".format(field_id), cursor))[0]
            is_pinned = list(helper.query("SELECT * FROM pin_unpin WHERE (user_id={0} AND field_id={1});".format(session["user_id"], field_id), cursor))
            match_ups = list(helper.query("SELECT * FROM matchups WHERE (field_id = {0});".format(field_id), cursor))
            match_up_list = []
            field_images = os.listdir(os.path.join(ROOT_DIR, "static/images/stadiums", str(field_id)))
            for match_up in match_ups:
                user = list(helper.query("SELECT * FROM users WHERE (user_id)={0};".format(match_up["challenger_id"]), cursor))[0]
                team = list(helper.query("SELECT * FROM teams WHERE (team_id)={0};".format(match_up["team_id"]), cursor))[0]
                request_to_joins = list(helper.query("SELECT * FROM request_to_join WHERE (match_id)={0};".format(match_up["match_id"]), cursor))
                requester_id_list = [requester["team_id"] for requester in request_to_joins]
                match_up_list.append({"username": user["username"],
                                      "avatar": user["avatar"],
                                      "team": team["team_name"],
                                      "start_time": helper.format_date(match_up["start_date"]) + "  " + helper.format_time(match_up["start_time"]),
                                      "end_time": helper.format_date(match_up["end_date"]) + "  " + helper.format_time(match_up["end_time"]),
                                      "comment": match_up["comment"],
                                      "match_id": match_up["match_id"],
                                      "is_joined": True if session["user_teams"][0]["team_id"] in requester_id_list else False,
                                      "request_num": len(requester_id_list)})
            return render_template("home.html", user_id = session["user_id"],
                                                user_avatar = session["user_avatar"],
                                                username = session["username"],
                                                user_teams = session["user_teams"],
                                                match_up_list = match_up_list,
                                                field={"field_id" : field_id,
                                                       "field_name": field["field_name"],
                                                       "field_image": "/static/images/stadiums/" + str(field_id) + "/" + field_images[0],
                                                       "open_time": field["open_time"],
                                                       "close_time": field["close_time"],
                                                       "is_pinned": True if is_pinned else False,
                                                        })
        else:
            return redirect(url_for("login"))
    elif request.method == "POST":
        if request.form["actionType"] == "pin":
            if request.form["action"] == "+":
                helper.update("INSERT INTO pin_unpin (user_id, field_id) VALUES ({0}, {1});".format(session["user_id"], field_id), cursor, db)
            else:
                helper.update("DELETE FROM pin_unpin WHERE(user_id={0} AND field_id={1});".format(session["user_id"], field_id), cursor, db)
        elif request.form["actionType"] == "join":
            match_up = list(helper.query("SELECT * FROM matchups WHERE(match_id={0});".format(request.form["match_id"]), cursor))[0]
            if match_up["team_id"] != int(request.form["team_id"]):
                if request.form["action"] == "+":
                    helper.update(" INSERT INTO request_to_join (team_id, match_id) VALUES ({0}, {1});".format(request.form["team_id"], request.form["match_id"]), cursor, db)
                else:
                    helper.update("DELETE FROM request_to_join WHERE(team_id={0} AND match_id={1});".format(request.form["team_id"], request.form["match_id"]), cursor, db)
                return dumps({"isSuccess": True})
            else:
                return dumps({"isSuccess": False})
        elif request.form["actionType"] == "changeSelect":
            teams = list(helper.query("SELECT * FROM request_to_join WHERE(team_id = {0} AND match_id={1});".format(request.form["team_id"], request.form["match_id"]), cursor))
            return dumps({"is_joined": True if len(teams) > 0 else False})
        elif request.form["actionType"] == "createMatch":
            helper.update("INSERT INTO matchups (challenger_id, field_id, team_id, start_date, end_date, start_time, end_time, comment) VALUES ({0}, {1}, {2}, '{3}', '{4}', '{5}', '{6}', '{7}');".
                          format(session["user_id"], field_id, request.form["team_id"], request.form["startDate"], request.form["endDate"],
                                 request.form["startTime"], request.form["endTime"], request.form["comment"]), cursor, db)
    return "Hello world"


@app.route("/return_fields", methods=["POST"])
def return_fields():
    if request.method == "POST":
        fields = list(helper.query("SELECT * FROM fields;", cursor))
        field_info = [{"field_id": field["field_id"], "lat": float(field["latitude"]), "lng": float(field["longtitude"])} for field in fields]
        return dumps(field_info)


@app.route("/return_teams", methods = ["POST"])
def return_teams():
    if request.method == "POST":
        return dumps(session["user_teams"])


# where field owners can set their price range, update their description etc
@app.route("/fieldowners")
def field_owner():
    return "Hello field owners"


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("user_avatar", None)
    session.pop("username", None)
    session.pop("user_teams", None)
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run()
