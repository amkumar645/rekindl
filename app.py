from flask import Flask, jsonify, request
import db
import helper

app = Flask(__name__)

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
    hobbies = data['hobbies'].split(",")
    db.user_collection.insert_one({
        "username": data['username'],
        "password": data['password'],
        "name": data['name'],
        "interests": interests,
        "hobbies": hobbies,
        "friends": [],
        "relationship": [],
        "last_time_friend_seen": [],
        "reminder_for_friend": []
    })
    return "Added User!"

# Update user
@app.route('/users/update/<username>', methods=['POST'])
def update_user(username):
    data = request.form
    db.user_collection.update_one(
    {
        'username': username
    },
    {
        "username": username,
        "password": data['password'],
        "name": data['name'],
        "interests": data['interests'],
        "hobbies": data['hobbies'],
        "friends": data['friends'],
        "relationship": [],
        "last_time_friend_seen": data['last_time_friend_seen'],
        "reminder_for_friend": data['reminder_for_friend']
    })
    return "Added User!"

if __name__ == '__main__':
    app.run(port=8000)
