from flask import *
from bson.json_util import dumps
import pymysql
from helper import *
import os
import random


app = Flask(__name__)
app.secret_key = "qwre953heqirhv3,;qgbh4549s/;,"
db = pymysql.connect(host="35.193.15.89",
                     user="root",
                     password="root",
                     db="soccerdb",
                     cursorclass=pymysql.cursors.DictCursor)

cursor = db.cursor()
ROOT_DIR = os.path.dirname(__file__)


@app.route("/")
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        user = query_one("SELECT * FROM users WHERE (username='{0}' AND password='{1}') OR (email='{0}' AND password='{1}') LIMIT 1;".
                             format(filter_sql(request.form["username"]), filter_sql(request.form["password"])), cursor)
        if user:
            session["user_id"] = user["user_id"]
            fields = query_all("SELECT * FROM pin_unpin WHERE (user_id={0});".format(session["user_id"]), cursor)
            if fields:
                field_id = random.choice(fields)["field_id"]
            else:
                fields = query_all("SELECT * FROM fields;", cursor)
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
            user = query_one("SELECT * FROM users WHERE (user_id = {0}) LIMIT 1;".format(session["user_id"]), cursor)
            session["user_avatar"] = user["avatar"]
            session["username"] = user["username"]
            user_team_ids = query_all("SELECT * FROM user_team_rela WHERE(user_id = {0});".format(session["user_id"]), cursor)
            user_team_ids = [team["team_id"] for team in user_team_ids]
            user_teams = [query_one("SELECT * FROM teams WHERE (team_id={0}) LIMIT 1;".format((team_id)), cursor) for team_id in user_team_ids]
            session["user_teams"] = [{"team_id" : user_team["team_id"],
                                      "team_name": user_team["team_name"],
                                      "team_logo": user_team["team_logo"]} for user_team in user_teams]
            field = query_one("SELECT * FROM fields WHERE (field_id={0}) LIMIT 1;".format(field_id), cursor)
            is_pinned = query_one("SELECT * FROM pin_unpin WHERE (user_id={0} AND field_id={1}) LIMIT 1;".format(session["user_id"], field_id), cursor)
            unseen_notification_num = len(query_all("SELECT * FROM notifications WHERE (user_id = {0} AND seen='F') ORDER BY updated_time DESC;".format(session["user_id"]), cursor))
            match_ups = query_all("SELECT * FROM matchups WHERE (field_id = {0}) ORDER BY updated_time DESC;".format(field_id), cursor)
            match_up_list = []
            field_images = os.listdir(os.path.join(ROOT_DIR, "static/images/stadiums", str(field_id)))
            for match_up in match_ups:
                user = query_one("SELECT * FROM users WHERE (user_id={0}) LIMIT 1;".format(match_up["challenger_id"]), cursor)
                team = query_one("SELECT * FROM teams WHERE (team_id={0}) LIMIT 1;".format(match_up["team_id"]), cursor)
                request_to_joins = query_all("SELECT * FROM request_to_join WHERE (match_id={0});".format(match_up["match_id"]), cursor)
                requester_id_list = [requester["team_id"] for requester in request_to_joins]
                match_up_list.append({"username": user["username"],
                                      "avatar": user["avatar"],
                                      "team": team["team_name"],
                                      "start_time": format_date(match_up["start_date"]) + "  " + format_time(match_up["start_time"]),
                                      "end_time": format_date(match_up["end_date"]) + "  " + format_time(match_up["end_time"]),
                                      "comment": match_up["comment"],
                                      "match_id": match_up["match_id"],
                                      "is_joined": True if session["user_teams"][0]["team_id"] in requester_id_list else False,
                                      "request_num": len(requester_id_list)})
            return render_template("home.html", user_id = session["user_id"],
                                                user_avatar = session["user_avatar"],
                                                username = session["username"],
                                                unseen_noti_num = unseen_notification_num,
                                                user_teams = session["user_teams"],
                                                match_up_list = match_up_list,
                                                field={"field_id" : field_id,
                                                       "field_name": field["field_name"],
                                                       "field_image": "/static/images/stadiums/" + str(field_id) + "/" + field_images[0],
                                                       "open_time": field["open_time"],
                                                       "close_time": field["close_time"],
                                                       "is_pinned": True if is_pinned else False
                                                        })
        else:
            return redirect(url_for("login"))
    elif request.method == "POST":
        if request.form["actionType"] == "pin":
            if request.form["action"] == "+":
                update("INSERT INTO pin_unpin (user_id, field_id) VALUES ({0}, {1});".format(session["user_id"], field_id), cursor, db)
            else:
                update("DELETE FROM pin_unpin WHERE(user_id={0} AND field_id={1});".format(session["user_id"], field_id), cursor, db)
        elif request.form["actionType"] == "join":
            match_up = query_one("SELECT * FROM matchups WHERE(match_id={0}) LIMIT 1;".format(request.form["match_id"]), cursor)
            if match_up["team_id"] != int(request.form["team_id"]):
                if request.form["action"] == "+":
                    update(" INSERT INTO request_to_join (team_id, match_id) VALUES ({0}, {1});".format(request.form["team_id"], request.form["match_id"]), cursor, db)
                    team = query_one("SELECT * FROM teams WHERE (team_id={0}) LIMIT 1;".format(request.form["team_id"]), cursor)
                    field_name = query_one("SELECT * FROM fields WHERE (field_id={0}) LIMIT 1;".format(match_up["field_id"]), cursor)["field_name"]
                    noti_content = "Team {0} requests to join your game at {1} from {2} {3} to {4} {5}".format(team["team_name"], field_name, str(match_up["start_time"]), str(match_up["start_date"]), str(match_up["end_time"]), str(match_up["end_date"]))
                    update("INSERT INTO notifications (user_id, content, image) VALUES ({0}, '{1}', '{2}');".format(session["user_id"], filter_sql(noti_content), "/team_logos/" + team["team_logo"]), cursor, db)
                else:
                    update("DELETE FROM request_to_join WHERE(team_id={0} AND match_id={1});".format(request.form["team_id"], request.form["match_id"]), cursor, db)
                return dumps({"isSuccess": True})
            else:
                return dumps({"isSuccess": False})
        elif request.form["actionType"] == "changeSelect":
            teams = query_all("SELECT * FROM request_to_join WHERE(team_id = {0} AND match_id={1});".format(request.form["team_id"], request.form["match_id"]), cursor)
            return dumps({"is_joined": True if len(teams) > 0 else False})
        elif request.form["actionType"] == "createMatch":
            update("INSERT INTO matchups (challenger_id, field_id, team_id, start_date, end_date, start_time, end_time, comment) VALUES ({0}, {1}, {2}, '{3}', '{4}', '{5}', '{6}', '{7}');".
                          format(session["user_id"], field_id, request.form["team_id"], filter_sql(request.form["startDate"]), filter_sql(request.form["endDate"]),
                                 filter_sql(request.form["startTime"]), filter_sql(request.form["endTime"]), filter_sql(request.form["comment"])), cursor, db)
            list_of_users = query_all("SELECT * FROM pin_unpin WHERE (field_id = {0});".format(field_id), cursor)
            field = query_one("SELECT * FROM fields WHERE (field_id={0}) LIMIT 1;".format(field_id), cursor)
            team = query_one("SELECT * FROM teams WHERE (team_id = {0}) LIMIT 1;".format(request.form["team_id"]), cursor)
            noti_content = "A new game has been created at {0} by {1}, from {2} {3} to {4} {5}".format(field["field_name"],
                                                                                                       team["team_name"],
                                                                                                       request.form["startTime"],
                                                                                                       request.form["startDate"],
                                                                                                       request.form["endTime"],
                                                                                                       request.form["endDate"])
            for user in list_of_users:
                update("INSERT INTO notifications (user_id, content, image) VALUES ({0}, '{1}', '{2}');".format(user["user_id"], filter_sql(noti_content), "/team_logos/" + team["team_logo"]), cursor, db)
    return "Hello world"


@app.route("/return_fields", methods=["POST"])
def return_fields():
    if request.method == "POST":
        fields = query_all("SELECT * FROM fields;", cursor)
        field_info = [{"field_id": field["field_id"], "lat": float(field["latitude"]), "lng": float(field["longtitude"])} for field in fields]
        return dumps(field_info)


@app.route("/return_teams", methods = ["POST"])
def return_teams():
    if request.method == "POST":
        return dumps(session["user_teams"])


@app.route("/return_matchups", methods=["POST"])
def return_matchups():
    if request.method == "POST":
        return


@app.route("/return_notifications", methods=["POST"])
def return_notifications():
    if request.method == "POST":
        if request.form["actionType"] == "get_noti":
            notifications = query_all("SELECT * FROM notifications WHERE (user_id = {0}) ORDER BY updated_time DESC LIMIT 10;".format(session["user_id"]), cursor)
            update("UPDATE notifications SET seen = 'T' WHERE (user_id = {0});".format(session["user_id"]), cursor, db)
            return dumps([{"noti_id": notification["notification_id"],
                           "noti_content": notification["content"],
                           "noti_image": notification["image"],
                           "updated_time": notification["updated_time"]} for notification in notifications])
        else:
            return dumps({"new_noti": len(query_all("SELECT * FROM notifications WHERE (user_id = {0} AND seen='F') ORDER BY updated_time DESC;".format(session["user_id"]), cursor))})


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
