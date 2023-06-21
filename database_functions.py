import json


def add_user_to_db(author_id,user_Name):
    auth_id = str(author_id)
    with open('E:\python bot\AnimeQuizBot\database.json', 'r') as f:
        data = json.load(f)
        if data.get(auth_id) is None:
            data[auth_id] = {
                "Name": user_Name,
                "points": 0,
            }
        else:
            return
    with open('E:\python bot\AnimeQuizBot\database.json', 'w') as f:
        try:
            json.dump(data, f, indent=4)
        except Exception as e:
            print(e)


def add_points(author_id, point_amount, user_Name):
    add_user_to_db(author_id,user_Name)
    auth_id = str(author_id)
    data = {}
    with open('E:\python bot\AnimeQuizBot\database.json', 'r') as f:
        data = json.load(f)

    data[auth_id]["points"] += point_amount

    with open('E:\python bot\AnimeQuizBot\database.json', 'w') as f:
        try:
            json.dump(data, f, indent=4)
        except Exception as e:
            print(e)


def get_points(discord_id):
    auth_id = str(discord_id)
    points = 0
    try:
        with open('E:\python bot\AnimeQuizBot\database.json', 'r') as f:
            json_data = json.load(f)
            if json_data.get(auth_id) is None:
                return 0
            points = json_data[auth_id]['points']
    except Exception as e:
        print(e)

    return points

def get_stats():
    with open('E:\python bot\AnimeQuizBot\database.json', 'r') as f:
        json_data=json.load(f)
        sorted_data = dict(sorted(json_data.items(), key=lambda x: x[1]["points"], reverse=True))
        return sorted_data



