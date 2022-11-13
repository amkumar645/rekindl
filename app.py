from flask import Flask, jsonify, request
import db
import helper
import spacy
import pickle
import numpy as np
from datetime import date, datetime
from flask_cors import CORS, cross_origin


app = Flask(__name__)
CORS(app)

nlp = pickle.load(open('nlp_md.pkl', 'rb'))

@app.route('/', methods=['GET'])
def index():
    return "WELCOME TO REKINDL API"

# Get user
@app.route('/users/<username>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_user(username):
    user = db.user_collection.find_one({'username': username})
    user_json = helper.get_json_for_user(user)
    return jsonify(user_json)

# Get all users
@app.route('/users/all', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_all_users():
    users = db.user_collection.find()
    users_json = []
    for user in users:
        users_json.append(helper.get_json_for_user(user))
    return jsonify(users_json)

# Add user
@app.route('/users/add', methods=['POST'])
@cross_origin(supports_credentials=True)
def add_user():
    data = request.form
    interests = data['interests'].split(",")
    print(type(data['birthday']))
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
@cross_origin(supports_credentials=True)
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
@cross_origin(supports_credentials=True)
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

# Match user to a friend based on criteria
@app.route('/match/<username>', methods=['GET'])
@cross_origin(supports_credentials=True)
def find_match(username):
    familiarity = int(request.args.get('fam'))
    topic = request.args.get('topic')
    user = db.user_collection.find_one({'username': username})
    friends = []
    # Get list of all friends
    for i, friend in enumerate(user['friends']):
        friend_det = db.user_collection.find_one({'username': friend})
        friends.append([friend_det, user['last_time_friend_seen'][i]])
    # Sort friends by familiarity
    # If they chose unfamiliar, get someone they haven't talked to in a while
    if familiarity == 0:
        friends.sort(key=lambda x: x[1], reverse=True)
    else:
        friends.sort(key=lambda x: x[0], reverse=True)
    # Then check for topics in common between interests with NLP

# Get all users
@app.route('/match/interests/<username>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_interests(username):
    user = db.user_collection.find_one({'username': username})
    interests = user['interests']

    otherUsername = request.args.get('otherUsername')
    otherUsernameUser = db.user_collection.find_one({'username': otherUsername})
    otherUserInterests = otherUsernameUser['interests']

    def common_interests(p1, p2):
        w = [9.05503054, -4.69843102]      # from logistic regression in nlp_testing.py
        m = len(p1)
        n = len(p2)
        common_interests = []
        common_similarities = []
        for i in range(m):
            for j in range(n):
                similarity = nlp(p1[i]).similarity(nlp(p2[j]))
                if w[0] * similarity + w[1] >= 0:
                    common_interests.append((p1[i], p2[j]))
                    common_similarities.append(similarity)
        
        num_common = len(common_interests)
        top_two = []
        if num_common > 0:
            max_index = np.argmax(common_similarities)
            top_two.append(common_interests[max_index])
            common_similarities[max_index] = -1
            if num_common > 1:
                next_max_index = np.argmax(common_similarities)
                top_two.append(common_interests[next_max_index])
        
        return top_two
    
    common_interests = common_interests(interests, otherUserInterests)
    
    comm_json = {
        'common_interests' :  [common_interests[0], common_interests[1]]
    }

    # database update
    sortedNames = [username, otherUsername]
    sortedNames.sort()

    # determine if database already contains the pair
    if(db.common_interests_collection.count_documents({"userNameCombo": sortedNames[0] + sortedNames[1]}) == 0):
        db.common_interests_collection.insert_one({
            "userNameCombo": sortedNames[0] + sortedNames[1],
            "common_interests": [common_interests[0], common_interests[1]],
        })

    else:
        db.common_interests_collection.update_one({"userNameCombo": sortedNames[0] + sortedNames[1]}, {"$set":{
            "userNameCombo": sortedNames[0] + sortedNames[1],
            "common_interests": [common_interests[0], common_interests[1]],
        }})
        
    return jsonify(comm_json)

if __name__ == '__main__':
    app.run(port=10001, debug=True)
