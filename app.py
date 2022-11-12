from flask import Flask
import db

app = Flask(__name__)

@app.route('/')
def flask_mongodb_atlas():
    return "flask mongodb atlas!"

#test to insert data to the data base
@app.route("/test")
def test():
    db.user_collection.insert_one({
        "username": "amkumar",
        "password": "password",
        "name": "Arnav Kumar",
        "interests": ["Sports", "Cats"],
        "hobbies": ["Bowling", "Arcades"],
        "friends": [],
        "last_time_friend_seen": [],
        "reminder_for_friend": []
    })
    return "Connected to the data base!"

if __name__ == '__main__':
    app.run(port=8000)
