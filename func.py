import json

def load_data():
    try:
        f = open("users.json", "r+", encoding='utf-8')
        user_data = json.load(f, ensure_ascii=False)
        f.close()
        return user_data
    except Exception as ex:
        user_data = {}
        return user_data

def save_data(user_data):
    with open("users.json", 'w', encoding='utf-8') as f:
        json.dump(user_data, f, indent=4, ensure_ascii=False)
