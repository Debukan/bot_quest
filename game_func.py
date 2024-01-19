import json

# считывание локаций квеста
def get_game_data():
    f = open("game.json", "r+", encoding='utf-8')
    game_data = json.load(f)
    f.close()
    return game_data



