def list_to_string(list):
    s = ''
    for item in list:
        s += item + ','
    return s[:-1]

def list_to_string_friends(list):
    s = ''
    for item in list:
        s += item + '_'
    return s[:-1]

def get_json_for_user(user):
    user_json = {
        'username': user['username'],
        'password': user['password'],
        'name': user['name'],
        "location": user['location'],
        "birthday": user['birthday'],
        'interests': list_to_string(user['interests']),
        'friends': list_to_string_friends(user['friends']),
        'last_time_friend_seen': list_to_string_friends(user['last_time_friend_seen']),
        'reminder_for_friend': list_to_string_friends(user['reminder_for_friend']),
    }
    return user_json