from flask import Flask, jsonify, request
import db
import helper
import spacy
import pickle
from datetime import date, datetime


app = Flask(__name__)

# nlp = pickle.load(open('npl_md.pkl', 'rb'))

@app.route('/', methods=['GET'])
def index():
    return "WELCOME TO REKINDL API"

# Get user
@app.route('/users/<username>', methods=['GET'])
def get_user(username):
    user = db.user_collection.find_one({'username': username})
    user_json = helper.get_json_for_user(user)
    return jsonify(user_json)

# Get all users
@app.route('/users/all', methods=['GET'])
def get_all_users():
    users = db.user_collection.find()
    users_json = []
    for user in users:
        users_json.append(helper.get_json_for_user(user))
    return jsonify(users_json)

# Add user
@app.route('/users/add', methods=['POST'])
def add_user():
    data = request.form
    interests = data['interests'].split(",")
    db.user_collection.insert_one({
        "username": data['username'],
        "password": data['password'],
        "name": data['name'],
        "location": data['location'],
        "birthday": data['birthday'],
        "interests": interests,
        "friends": [],
        "last_time_friend_seen": [],
        "reminder_for_friend": [],
    })
    return "Added User!"

# Update user
@app.route('/users/update/<username>', methods=['POST'])
def update_user(username):
    data = request.form
    interests = data['interests'].split(",")
    friends = data['friends'].split("_")
    last_time_friend_seen = data['last_time_friend_seen'].split("_")
    reminder_for_friend = data['reminder_for_friend'].split("_")
    filter = {"username": username}
    new_vals = { "$set":
        {
            "username": username,
            "password": data['password'],
            "name": data['name'],
            "location": data['location'],
            "birthday": data['birthday'],
            "interests": interests,
            "friends": friends,
            "last_time_friend_seen": last_time_friend_seen,
            "reminder_for_friend": reminder_for_friend
        }
    }
    db.user_collection.update_one(filter, new_vals)
    return "Updated User!"

# Get upcoming deadlines for a user's friends
@app.route('/upcoming/<username>', methods=['GET'])
def upcoming_friends(username):
    today = date.today()
    today = datetime.strptime(str(today), "%Y-%m-%d")
    user = db.user_collection.find_one({'username': username})
    late_friends = []
    for i, last_seen in enumerate(user['last_time_friend_seen']):
        last_seen_date = datetime.strptime(last_seen, "%Y-%m-%d")
        threshold = user['reminder_for_friend'][i]
        dist = (today - last_seen_date).days - int(threshold)
        if dist >= 0:
            overall_info = [dist, user['friends'][i]]
            late_friends.append(overall_info)
    late_friends.sort(key=lambda x: x[0], reverse=True)
    friends_json = []
    for friend in late_friends[0:1]:
        user = db.user_collection.find_one({'username': friend[1]})
        friends_json.append(helper.get_json_for_user(user))
    return jsonify(friends_json[0:3])



if __name__ == '__main__':
    app.run(port=8000, debug=True)
