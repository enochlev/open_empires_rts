from flask import Flask, render_template, request, redirect, url_for, session, Blueprint, flash
#from player import Player, quests, global_trades,game_config
from app.db_utils import game_config, GameAPI, PlayerAPI
import os
import json
import smtplib
import dotenv
dotenv.load_dotenv()
import datetime
import os
import base64
from werkzeug.security import generate_password_hash, check_password_hash
import time

SPEED = 3.5

extra_url = "/empire-game"
app = Flask(__name__, static_url_path=extra_url +'/static')
empire_game_bp = Blueprint('empire_game', __name__, url_prefix=extra_url)
app.secret_key = 'your_secret_key'  # Replace with a real secret key
# Dictionary to store players by name
game_api = GameAPI()

# ---------- Token utilities for password reset ----------
def generate_reset_token(email):
    """
    This example simply base64-encodes the email and current UTC time.
    For production, use a proper token serializer (like itsdangerous.URLSafeTimedSerializer).
    """
    token_data = f"{email}:{datetime.datetime.utcnow()}"
    token = base64.urlsafe_b64encode(token_data.encode()).decode()
    return token

def verify_reset_token(token):
    """
    Decode the token and return the email if successful.
    (This simple example does not check expiry.)
    """
    try:
        token_bytes = base64.urlsafe_b64decode(token.encode())
        token_str = token_bytes.decode()
        email, _ = token_str.split(":", 1)
        return email
    except Exception:
        return None

    # ---------- Email sending function ----------
def send_password_reset_email(email, token):
    from_email = 'enochlev@icloud.com'
    to_email = email
    domain_name = 'https://enochlev.com/empire-game'

    smtp_obj = smtplib.SMTP('smtp.mail.me.com', 587)
    smtp_obj.starttls()
    smtp_obj.login('enochlev@icloud.com', os.getenv('EMAIL_PASSWORD'))

    message = (f"From: {from_email}\r\nTo: {to_email}\r\n\r\n")
    message += (f"Subject: Password Reset\n\n"
                f"Click the link to reset your password: {domain_name}/reset-password/{token}")

    try:
        smtp_obj.sendmail(from_addr=from_email, to_addrs=to_email, msg=message)
    except Exception as e:
        print("Error sending email:", e)
    finally:
        smtp_obj.quit()


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


# ---------- Main route: Login, Sign-Up, and Reset Request ----------
@empire_game_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'login':
            # Login: one field (identifier) can be username or email.
            identifier = request.form.get('identifier')
            password = request.form.get('password')
            if not identifier or not password:
                flash("Please enter both identifier and password.", "error")
                return redirect(url_for('empire_game.index'))
            
            # Look up the player by username OR email.
            row = game_api.verify_valid_new_username_and_email(identifier, identifier)

            if not row:
                flash("User not found.", "error")
                return redirect(url_for('empire_game.index'))
            player_id = row['player_id']
            player_name = row['name']
            
            # Here, generate a session token as needed.
            session_token = game_api.create_session(player_id, password)
            if not session_token:
                flash("Invalid password.", "error")
                return redirect(url_for('empire_game.index'))

            session['current_player'] = player_name
            session['current_player_id'] = player_id
            session['session_oath'] = session_token
            game_api.update_progress(player_id)
            return redirect(url_for('empire_game.dashboard'))
        
        elif action == 'signup':
            # Sign Up: requires username, email, and password.
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            if not username or not email or not password:
                flash("Please fill in all fields for sign up.", "error")
                return redirect(url_for('empire_game.index'))
            
            # Check if the username already exists.
            row = game_api.verify_valid_new_username_and_email(username, email)
            
            if row != None:
                player_id = row['player_id']
                stored_email = row['email']
                stored_name = row['name']

                if stored_email == email:
                    flash("Email is already in use.", "error")
                if stored_name == username:
                    flash("Username is already in use.", "error")
                
                #dont return anything, just flash the error
                return redirect(url_for('empire_game.index'))

            else:
                # Create a new player.
                player_id = game_api.add_new_player(username, password, email)
            
            
            session_token = game_api.create_session(player_id, password)
            session['current_player'] = username
            session['current_player_id'] = player_id
            session['session_oath'] = session_token
            game_api.update_progress(player_id)
            return redirect(url_for('empire_game.dashboard'))
        
        elif action == 'reset_request':
            # Reset Password Request: just need email.
            reset_email = request.form.get('email')
            if not reset_email:
                flash("Please enter your email address.", "error")
                return redirect(url_for('empire_game.index'))
            token = generate_reset_token(reset_email)
            send_password_reset_email(reset_email, token)
            flash("If the email is registered, a reset link has been sent.", "info")
            return redirect(url_for('empire_game.index'))
    
    # GET – render the login page with three tabs.
    return render_template('login.html')

# ---------- Reset Password Endpoint ----------
@empire_game_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    
    email = verify_reset_token(token)
    if not email:
        flash("Invalid or expired token.", "error")
        return redirect(url_for('empire_game.index'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        if new_password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for('empire_game.reset_password', token=token))
        
        # Update the password in the DB for the user with this email.

        game_api.reset_password(email, new_password)

        flash("Your password has been reset. Please log in.", "success")
        return redirect(url_for('empire_game.index'))
    
    return render_template('reset_password.html', token=token)

# (Also ensure that you have a route for game_api.dashboard and configure your Flask app for sessions and flash messages.)



@empire_game_bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    
    player_name = session.get('current_player')
    player_id = session.get('current_player_id')

    validation = game_api.validate_session(session.get('current_player_id'), session.get('session_oath'))
    if validation is None:
        return redirect(url_for('empire_game.index'))


    player_api = PlayerAPI(player_id) 

    game_api.update_progress(player_id)
    player_data = player_api.load_player_stats()
    

    message = None
    if request.method == 'POST':
        if 'purchase_unit' in request.form:
            #if "barracks_unit_type" in request.form:
            message = player_api.purchase_unit(request.form.get('unit_type'))
        elif 'remove_unit_from_queue' in request.form:
            message = player_api.remove_unit_from_queue(request.form.get('unit_type'))
        elif 'purchase_building' in request.form:
            message = player_api.purchase_building(request.form.get('building_type'))
        elif 'upgrade_unit' in request.form:
            message = player_api.upgrade_unit(request.form.get('unit_type'))
        elif 'add_worker' in request.form:
            message = player_api.add_worker(request.form.get('building_type'))
        elif 'remove_worker' in request.form:
            message = player_api.remove_worker(request.form.get('building_type'))
        elif 'add_trade_offer' in request.form:
            resources_cost = {request.form.get('resources_cost'): int(request.form.get('cost_amount'))}
            resources_earned = {request.form.get('resources_earned'): int(request.form.get('earned_amount'))}
            message = player_api.add_trade_offer(resources_cost, resources_earned)
        elif 'remove_trade_offer' in request.form:
            trade_index = int(request.form.get('trade_index'))
            
            trades = player_data["Trades"]
            for i in range(len(trades)):
                if trades[i]["player"] != player_name:
                    trade_index -= 1
                else:
                    break

            message = player_api.remove_trade_offer(trade_index)


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


        game_api.update_progress(player_id)
        flash(message)
        return redirect(url_for('empire_game.dashboard'))
    
        # Add more POST request handling for other actions like adding/removing citizens, miners, etc.


        
    #message = session.pop('message', None)

    render_data = {
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
    
    # with open("building_map.json") as f:
    #     building_map = json.load(f)

    # for building in player.player_stats["Buildings"]["levels"]:
    #     level = player.player_stats["Buildings"]["levels"][building]
    #     if level > 0:
    #         id = building + str(level)
    #         if id in building_map: 
    #             #print(building_map[id])
    #             game_data["buildings"].append(building_map[id]) 

    return render_template('dashboard.html', player_data=player_data, game_config=game_config, render_data=render_data)

# Additional routes for specific actions like adding/removing miners, managing farms, etc.

# def periodic_task():
#     for player_ in players:
#         players[player_].update(SPEED)
#     save_progress()

# def save_progress():
#     jsonFile = []
#     for player in players:
#         jsonFile.append(players[player].export_player_values())
    
#     if len(jsonFile) > 0:
#         with open("progress.json", "w") as f:
#             json.dump({'progress':jsonFile}, f)
    
#     #randomly backup every 1/100 chance using random
#     import random
#     if random.randint(0,100) == 0:
#         with open("progress_backup.json", "w") as f:
#             json.dump({'progress':jsonFile}, f)

# from apscheduler.schedulers.background import BackgroundScheduler
# import atexit
# scheduler = BackgroundScheduler()
# scheduler.add_job(func=periodic_task, trigger="interval", seconds=10)
# scheduler.start()


if __name__ == '__main__':
    app.register_blueprint(empire_game_bp)
    app.run(host='0.0.0.0', port=8000, debug=True)
#https://chat.openai.com/share/c680c458-34b7-4287-b80c-5f3b1b21d50e