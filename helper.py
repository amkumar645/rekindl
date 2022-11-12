def list_to_string(list):
    s = ''
    for item in list:
        s += item + ','
    return s[:-1]

def get_json_for_user(user):
    user_json = {
        'username': user['username'],
        'password': user['password'],
        'name': user['name'],
        'interests': list_to_string(user['interests']),
        'hobbies': list_to_string(user['hobbies']),
        'friends': list_to_string(user['friends']),
        'last_time_friend_seen': list_to_string(user['last_time_friend_seen']),
        'reminder_for_friend': list_to_string(user['reminder_for_friend'])
    }
    return user_json
