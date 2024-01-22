import json

def load_data(path):
    try:
        f = open(path, "r+", encoding='utf-8')
        data = json.load(f)
        f.close()
        return data
    except Exception as ex:
        data = {}
        return data

def save_data(user_data):
    with open("users.json", 'w', encoding='utf-8') as f:
        json.dump(user_data, f, indent=4, ensure_ascii=False)
