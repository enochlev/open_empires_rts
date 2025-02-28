from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
from player import Player, quests, global_trades,game_config
import os
import json
SPEED = 3.5

extra_url = "/empire-game"
app = Flask(__name__, static_url_path=extra_url +'/static')
empire_game_bp = Blueprint('empire_game', __name__, url_prefix=extra_url)
app.secret_key = 'your_secret_key'  # Replace with a real secret key
# Dictionary to store players by name
players = {}


map_config = {
    "image_file": "game_map.png",
    "nodes": [
        {
            "id": 1,
            "x": 123,
            "y": 232,
            "size": 1,
            "connected_ids": [2, 3],
            "connected_ids_water": [4]
        },
        {
            "id": 2,
            "x": 234,
            "y": 345,
            "size": 1,
            "connected_ids": [1, 3, 4],
            "connected_ids_water": []
        },
        {
            "id": 3,
            "x": 345,
            "y": 456,
            "size": 1,
            "connected_ids": [1, 2, 4],
            "connected_ids_water": []
        },
        {
            "id": 4,
            "x": 456,
            "y": 567,
            "size": 1,
            "connected_ids": [2, 3, 5],
            "connected_ids_water": [1]
        },
        {
            "id": 5,
            "x": 567,
            "y": 678,
            "size": 1,
            "connected_ids": [4, 6],
            "connected_ids_water": []
        },
        {
            "id": 6,
            "x": 678,
            "y": 789,
            "size": 1,
            "connected_ids": [5, 7],
            "connected_ids_water": []
        },
        {
            "id": 7,
            "x": 789,
            "y": 890,
            "size": 1,
            "connected_ids": [6, 8],
            "connected_ids_water": []
        },
        {
            "id": 8,
            "x": 890,
            "y": 901,
            "size": 1,
            "connected_ids": [7],
            "connected_ids_water": []
        }
    ]
}


@app.route('/')
def home_redirect():
    return redirect(url_for('empire_game.index'))

@empire_game_bp.route('/', methods=['GET', 'POST'])
def index():
    global SPEED
    # Load existing players from saved session
    if "progress.json" in os.listdir():
        with open("progress.json") as f:
            jsonL = json.load(f)
            for player in jsonL["progress"]:
                playerObj = Player(load_config=player)
                players[playerObj.player_stats["Name"]] = playerObj

    if request.method == 'POST':
        player_name = request.form.get('player_name')
        if player_name:
            if player_name not in players:
                players[player_name] = Player(player_name)
            session['current_player'] = player_name
            return redirect(url_for('empire_game.dashboard'))
        
        new_speed = SPEED#request.form.get('speed')
        #new_speed = SPEED
        if new_speed:
            SPEED = int(new_speed)
            # You might want to add some logic to update anything dependent on SPEED here
            #return redirect(url_for('index'))

    

    

    map_data = {
        "main_image": "map.jpg",
        "players": [
            {"path": "castle1.png", "x": 10, "y": 20,"scale":.7},
            {"path": "Quarry3.png", "x": 915, "y": 15,"scale":.3},
            # ... more buildings
        ]
    }
    return render_template('index.html', current_players=list(players.keys()), current_speed = SPEED,render=map_data)

@empire_game_bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    
    player_name = session.get('current_player')
    if not player_name or player_name not in players:
        return redirect(url_for('empire_game.index'))

    player = players[player_name]

    player.update(SPEED)

    updated_quests = []
    #enumrate to get index and quest
    for quest_id in range(len(quests)):
        quest_copy = quests[quest_id].copy()
        quest_copy['completed'] = player.player_stats["Quests"][quest_id]
        updated_quests.append(quest_copy)

    #list of dicts
    trades = global_trades.copy()
    for trade in trades:
        trade["player"] = "global"
        
    for player_ in players:
        #exclude current player
        for trade in players[player_].player_stats["Market"]["listings"]:
            trade["player"] = player_
            trades.append(trade)

    message = None
    if request.method == 'POST':
        if 'purchase_unit' in request.form:
            if "barracks_unit_type" in request.form:
                message = player.purchase_unit(request.form.get('barracks_unit_type'))
            else:
                message = player.purchase_unit(request.form.get('unit_type'))
        elif 'remove_unit_from_queue' in request.form:
            message = player.remove_unit_from_queue(request.form.get('unit_type'))
        elif 'purchase_building' in request.form:
            message = player.purchase_building(request.form.get('building_type'))

        elif 'upgrade_unit' in request.form:
            message = player.upgrade_unit(request.form.get('unit_type'))
        elif 'add_worker' in request.form:
            message = player.add_worker(request.form.get('building_type'))
        elif 'remove_worker' in request.form:
            message = player.remove_worker(request.form.get('building_type'))
        elif 'add_trade_offer' in request.form:
            resources_cost = {request.form.get('resources_cost'): int(request.form.get('cost_amount'))}
            resources_earned = {request.form.get('resources_earned'): int(request.form.get('earned_amount'))}
            message = player.add_trade_offer(resources_cost, resources_earned)
        elif 'remove_trade_offer' in request.form:
            trade_index = int(request.form.get('trade_index'))
            
            for i in range(len(trades)):
                if trades[i]["player"] != player_name:
                    trade_index -= 1
                else:
                    break

            message = player.remove_trade_offer(trade_index)


        elif 'accept_trade_offer' in request.form:
            trade_index = int(request.form.get('trade_index'))
            source_player = trades[trade_index]["player"]
            if source_player == "global":
                resources_earned = trades[trade_index]["resources_cost"]
                resources_cost = trades[trade_index]["resources_earned"]
                message = player.make_trade(resources_cost,resources_earned)

            elif source_player == player_name:
                #skip
                pass
            else:
                for i in range(len(trades)):
                    if trades[i]["player"] != source_player:
                        trade_index -= 1
                    else:
                        break
                players[source_player].accept_offer(trade_index, player)
                #player.accept_offer(trade_index, players[source_player])
    

        save_progress()
        # Redirect to the same route to prevent form resubmission and add/modify message to session
        session['message'] = message
        return redirect(url_for('empire_game.dashboard'))
    
        # Add more POST request handling for other actions like adding/removing citizens, miners, etc.
    player = players[player_name]

    periodic_task()
    message = session.pop('message', None)

    game_data = game_data = {
        "main_image": "background.png",
        "buildings": [
            #{"path": "Market1.png", "x": 800, "y": 500,"scale":.4},
            #{"path": "Quarry1.png", "x": 800, "y": 90,"scale":.3},
            # ... more buildings
        ],
        "armies":[{"size":1,}]

    }
    #read from json file bubilding_map.json

    session_map_config = {
        "cities": [
            {
                "id": 2,
                "player_id": 1,
                "size": 1
            }
            # Add more cities following the same format if needed.
        ],
        "units": [
            {
                "unit_id": 1,
                "position": 3,
                "player_id": 1,
                "size": 1,
                "type": "fleet",
                "progression": None
            },
            {
                "unit_id": 2,
                "position": (4, 3),  # Meaning moving from 4 to 3
                "player_id": 1,
                "size": 1,
                "type": "army",
                "progression": "80%"
            }
            # Continue adding units as needed, following the format above.
        ]
    }
    
    with open("building_map.json") as f:
        building_map = json.load(f)

    for building in player.player_stats["Buildings"]["levels"]:
        level = player.player_stats["Buildings"]["levels"][building]
        if level > 0:
            id = building + str(level)
            if id in building_map: 
                #print(building_map[id])
                game_data["buildings"].append(building_map[id]) 

    return render_template('dashboard.html', current_players=list(players.keys()),render=game_data, player=player.player_stats, quests=updated_quests, trades=trades, game_config=game_config, message = message)

# Additional routes for specific actions like adding/removing miners, managing farms, etc.

def periodic_task():
    for player_ in players:
        players[player_].update(SPEED)
    save_progress()

def save_progress():
    jsonFile = []
    for player in players:
        jsonFile.append(players[player].export_player_values())
    
    if len(jsonFile) > 0:
        with open("progress.json", "w") as f:
            json.dump({'progress':jsonFile}, f)
    
    #randomly backup every 1/100 chance using random
    import random
    if random.randint(0,100) == 0:
        with open("progress_backup.json", "w") as f:
            json.dump({'progress':jsonFile}, f)

from apscheduler.schedulers.background import BackgroundScheduler
import atexit
scheduler = BackgroundScheduler()
scheduler.add_job(func=periodic_task, trigger="interval", seconds=10)
scheduler.start()


if __name__ == '__main__':
    app.register_blueprint(empire_game_bp)
    app.run(host='0.0.0.0', port=8000, debug=False)
#https://chat.openai.com/share/c680c458-34b7-4287-b80c-5f3b1b21d50e