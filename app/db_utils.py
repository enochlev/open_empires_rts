import sqlite3
import datetime
import json
import uuid


game_config = {}
with open("default_game_config.json") as f:
    game_config = json.load(f)

def get_config_value_from_string(game_config, object_string):
    """
    object string example
    "Buildings.Village House"

    should get the value from the game_config["Buildings"]["Village House"]
    """
    object_list = object_string.split(".")
    current_value = game_config
    for object in object_list:
        current_value = current_value[object]
    return current_value

def game_config_check(game_config):
    assert "Buildings" in game_config, "Buildings not found in game config"
    assert "Units" in game_config, "Units not found in game config"
    assert "Resources" in game_config, "Resources not found in game config"
    assert "Quests" in game_config, "Quests not found in game config"
    assert "game_speed_and_multiplier" in game_config, "game_speed not found in game config"


    all_resources = game_config["Resources"].keys()
    all_buildings = game_config["Buildings"].keys()
    all_units = game_config["Units"].keys()

    #check to make sure upgrade costs, production costs, for units and buildings are defined

    for building in game_config["Buildings"]:
        assert "cost" in game_config["Buildings"][building], f"cost not found for {building}"
        assert "hourly_cost" in game_config["Buildings"][building], f"hourly_cost not found for {building}"
        assert "max_level" in game_config["Buildings"][building], f"max_level not found for {building}"
        assert "hours_to_build" in game_config["Buildings"][building], f"hours_to_build not found for {building}"
        assert "starting_level" in game_config["Buildings"][building], f"starting_level not found for {building}"

            #check to make sure each on does not have extra resource requirements
        for potential_bad_resrouce in game_config["Buildings"][building]["cost"].keys():
            assert potential_bad_resrouce in all_resources, f"Incorrect resource {potential_bad_resrouce} in {building} upgrade costs"
            #create a warning if costs is negative
            if game_config["Buildings"][building]["cost"][potential_bad_resrouce] < 0:
                print(f"WARNING: {building} has negative cost for {potential_bad_resrouce}. Players will gain resources when building this. Make sure this is intended")

        for potential_bad_resrouce in game_config["Buildings"][building]["hourly_cost"].keys():
            assert potential_bad_resrouce in all_resources, f"Incorrect resource {potential_bad_resrouce} in {building} hourly_costs"
            #create a warning if costs is positive
            if game_config["Buildings"][building]["hourly_cost"][potential_bad_resrouce] < 0:
                print(f"WARNING: {building} has negative hourly cost for {potential_bad_resrouce}. Players will make money hourly after building this. Make sure this is intended")


    for unit in game_config["Units"]:
        assert "cost" in game_config["Units"][unit], f"cost not found for {unit}"
        assert "hourly_cost" in game_config["Units"][unit], f"hourly_cost not found for {unit}"
        assert "hours_to_build" in game_config["Units"][unit], f"hours_to_build not found for {unit}"
        assert "attack" in game_config["Units"][unit], f"attack not found for {unit}"
        assert "defense" in game_config["Units"][unit], f"defense not found for {unit}"
        assert "archer_defense" in game_config["Units"][unit], f"archer_defense not found for {unit}"
        assert "calvary_defense" in game_config["Units"][unit], f"calvary_defense not found for {unit}"
        assert "building_source" in game_config["Units"][unit], f"building_source not found for {unit}"
        assert "upgrade_cost" in game_config["Units"][unit], f"upgrade_cost not found for {unit}"
        assert "starting_level" in game_config["Units"][unit], f"starting_level not found for {unit}"
        assert "max_level" in game_config["Units"][unit], f"max_level not found for {unit}"
        assert "start_amount" in game_config["Units"][unit], f"start_amount not found for {unit}"

        for potential_bad_resrouce in game_config["Units"][unit]["cost"].keys():
            assert potential_bad_resrouce in all_resources, f"Incorrect resource {potential_bad_resrouce} in {unit} production costs"
            #create a warning if costs is negative
            if game_config["Units"][unit]["cost"][potential_bad_resrouce] < 0:
                print(f"WARNING: {unit} has negative cost for {potential_bad_resrouce}. Players will gain resources when building this. Make sure this is intended")

        for potential_bad_resrouce in game_config["Units"][unit]["hourly_cost"].keys():
            assert potential_bad_resrouce in all_resources, f"Incorrect resource {potential_bad_resrouce} in {unit} hourly costs"   
            #create a warning if costs is positive
            if game_config["Units"][unit]["hourly_cost"][potential_bad_resrouce] < 0:
                print(f"WARNING: {unit} has negative hourly cost for {potential_bad_resrouce}. Players will make money hourly after building this. Make sure this is intended")



        for potential_bad_resrouce in game_config["Units"][unit]["upgrade_cost"].keys():
            assert potential_bad_resrouce in all_resources, f"Incorrect resource {potential_bad_resrouce} in {unit} upgrade costs"
            #create a warning if costs is negative
            if game_config["Units"][unit]["upgrade_cost"][potential_bad_resrouce] < 0:
                print(f"WARNING: {unit} has negative upgrade cost for {potential_bad_resrouce}. Players will gain resources when building this. Make sure this is intended")


    for quest in game_config["Quests"]:
        assert "id" in quest, f"id not found for {quest}"
        assert "text" in quest, f"text not found for {quest}"
        assert "reward" in quest, f"reward not found for {quest}"
        assert "func" in quest, f"func not found for {quest}"
        #check to make sure each on does not have extra resource requirements
        for potential_bad_item in quest["func"].split(" "):
            if "building" in potential_bad_item:
                potential_bad_item = potential_bad_item.split(".")[1]
                assert potential_bad_item in all_buildings, f"Incorrect building {potential_bad_item} in {quest} requirements"
            elif "resource" in potential_bad_item:
                potential_bad_item = potential_bad_item.split(".")[1]
                assert potential_bad_item in all_resources, f"Incorrect resource {potential_bad_item} in {quest} requirements"
            elif "unit" in potential_bad_item:
                potential_bad_item = potential_bad_item.split(".")[1]
                assert potential_bad_item in all_units, f"Incorrect unit {potential_bad_item} in {quest} requirements"

            #elfit it must only contain digits and >=< signs
            else:
                for char in potential_bad_item:
                   assert char in "1234567890<=>", f"Incorrect resource {potential_bad_item} in {quest} requirements"

        for potential_bad_item in quest["reward"].split(" "):
            if "resource" in potential_bad_item:
                potential_bad_item = potential_bad_item.split(".")[1]
                assert potential_bad_item in all_resources, f"Incorrect resource {potential_bad_item} in {quest} rewards"
            else:
                for char in potential_bad_item:
                   assert char in "1234567890=", f"Incorrect resource {potential_bad_item} in {quest} rewards"

    """
    {
        "global_speed": 1,
        "building_speed": 1, 
        "unit_speed": 1,
        "resource_speed": 1,
        "research_speed": 1,
        "unit_upgrade_cost_multiplier": 2.2,
        "unit_upgrade_boost_multiplier": 1.2,
        "building_upgrade_cost_multiplier": 2.2,
        "building_upgrade_boost_multiplier": 1.2
    }"""
    assert "global_speed" in game_config["game_speed_and_multiplier"], "global_speed not found in game config"
    assert "building_speed" in game_config["game_speed_and_multiplier"], "building_speed not found in game config"
    assert "unit_speed" in game_config["game_speed_and_multiplier"], "unit_speed not found in game config"
    assert "resource_speed" in game_config["game_speed_and_multiplier"], "resource_speed not found in game config"
    assert "research_speed" in game_config["game_speed_and_multiplier"], "research_speed not found in game config"
    assert "unit_upgrade_cost_multiplier" in game_config["game_speed_and_multiplier"], "unit_upgrade_cost_multiplier not found in game config"
    assert "unit_upgrade_boost_multiplier" in game_config["game_speed_and_multiplier"], "unit_upgrade_boost_multiplier not found in game config"
    assert "building_upgrade_cost_multiplier" in game_config["game_speed_and_multiplier"], "building_upgrade_cost_multiplier not found in game config"
    assert "building_upgrade_boost_multiplier" in game_config["game_speed_and_multiplier"], "building_upgrade_boost_multiplier not found in game config"

game_config_check(game_config)


DB_NAME = "empire-game.db"

generate_password_hash = lambda x: x + "_hashed" #placeholder


def init_db():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    # Enable foreign keys if needed:
    cur.execute("PRAGMA foreign_keys = ON;")

    all_resources = game_config["Resources"].keys()
    all_buildings = game_config["Buildings"].keys()
    all_units = game_config["Units"].keys()
    
    # Create a players table that includes a last_update field.
    # Players: add a password_hash column.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            password_hash TEXT,
            last_update TIMESTAMP DEFAULT (datetime('now'))
        );
    """)
    
    # Resources, buildings, units, trade offers, quests, production_queue tables...
    # (Assumed to be created as before.)
    
    # Sessions table. It records a player session with a unique session_auth token,
    # a creation time, and an expiration time (set here to 24 hours after creation).
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            session_auth TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT (datetime('now')),
            expires_at TIMESTAMP DEFAULT (datetime('now', '+24 hours')),
            FOREIGN KEY(player_id) REFERENCES players(player_id)
        );
    """)
    
    # A table to store resource counts for each player.

    # replace resource to be more dynamic
    resource_string = ""
    for resource in all_resources:
        #maybe dfault resources is extra, but we will reset it on new player creation
        default_value = str(int(game_config["Resources"][resource]["default_value"]))
        resource_string += f"{resource} INTEGER DEFAULT {default_value}, "
    resource_string = resource_string[:-2]

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS resources (
            resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            {resource_string},
            timestamp TIMESTAMP DEFAULT (datetime('now')),
            FOREIGN KEY(player_id) REFERENCES players(player_id)
        );
    """)
    
    # A table for player buildings. For each building you can store:
    # level, any ongoing build progress (a float between 0 and 1) and a timestamp.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS buildings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            building_type TEXT,
            level INTEGER DEFAULT 0,
            ongoing_build_progress REAL,  -- NULL if not building
            timestamp TIMESTAMP DEFAULT (datetime('now')),
            FOREIGN KEY(player_id) REFERENCES players(player_id)
        );
    """)
    
    # A table for units. It contains unit counts, unit levels, any current production progress,
    # and a “queued” amount (how many are waiting “behind” the current production).
    cur.execute("""
        CREATE TABLE IF NOT EXISTS units (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            unit_type TEXT,
            count INTEGER DEFAULT 0,
            level INTEGER DEFAULT 0,
            ongoing_production_progress REAL,  -- NULL means not currently in production
            queued_count INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT (datetime('now')),
            FOREIGN KEY(player_id) REFERENCES players(player_id)
        );
    """)
    
    # A table for trade offers (storing JSON strings for costs/rewards is one simple approach)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trade_offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            resources_cost TEXT,  -- e.g., {"money": 100, "stone":10} as JSON text
            resources_earned TEXT,
            timestamp TIMESTAMP DEFAULT (datetime('now')),
            FOREIGN KEY(player_id) REFERENCES players(player_id)
        );
    """)
    
    # A table for quests, if you want to track completion per quest per player.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            quest_index INTEGER,
            completed BOOLEAN DEFAULT 0,
            timestamp TIMESTAMP DEFAULT (datetime('now')),
            FOREIGN KEY(player_id) REFERENCES players(player_id)
        );
    """)
    
    # A table for upgrades/production queues.
    # This table can serve several purposes: it allows you to record when a production (either a building upgrade or a unit production)
    # started, how long it takes (duration), and any queued orders.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS production_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            production_type TEXT,      -- 'building' or 'unit'
            entity TEXT,               -- which building (e.g., 'Barracks') or unit (e.g., 'Soldier')
            start_time TIMESTAMP DEFAULT (datetime('now')),
            duration REAL,             -- expected duration (in seconds, or hours) needed to complete
            progress REAL DEFAULT 0,     -- a float tracking current progress between 0 and 1
            status TEXT DEFAULT 'in_progress',  -- could be in_progress, completed, or queued
            FOREIGN KEY(player_id) REFERENCES players(player_id)
        );
    """)
    
    con.commit()
    con.close()




def add_new_player(name, plain_password):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    
    password_hash = generate_password_hash(plain_password)
    cur.execute("""
        INSERT OR IGNORE INTO players (name, password_hash, last_update)
        VALUES (?, ?, datetime('now'))
    """, (name, password_hash))
    con.commit()

    if False:
        #querry all hashed passwords
        out = cur.execute("SELECT * FROM players")
        for row in out:
            print(row)

    # Get the player_id for further reference.
    cur.execute("SELECT player_id FROM players WHERE name = ?", (name,))
    row = cur.fetchone()
    if not row:
        con.close()
        return None
    player_id = row[0]
    
    # Insert default resource values based on your in-memory defaults.
    # You can adjust these defaults as needed.
    #make this dynamic
    resource_string = ""
    value_string = ""
    for resource in game_config["Resources"]:
        resource_string += f"{resource}, "
        value_string += f"{game_config['Resources'][resource]['default_value']}, "
    resource_string = resource_string[:-2]
    value_string = value_string[:-2]
    
    cur.execute(f"""
        INSERT INTO resources (player_id, {resource_string}, timestamp)
        VALUES (?, {value_string}, datetime('now'))
    """, (player_id,))

    

    for building in game_config["Buildings"].keys():
        cur.execute("""
            INSERT INTO buildings (player_id, building_type, level, ongoing_build_progress)
            VALUES (?, ?, ?, NULL)
        """, (player_id, building, game_config["Buildings"][building]["starting_level"]))


    for unit in game_config["Units"].keys():
        cur.execute("""
            INSERT INTO units (player_id, unit_type, count, level, ongoing_production_progress, queued_count)
            VALUES (?, ?, ?, ?, NULL, 0)
        """, (player_id, unit, game_config["Units"][unit]["start_amount"], game_config["Units"][unit]["starting_level"]))
    

    for quest in game_config["Quests"]:
        cur.execute("""
            INSERT INTO quests (player_id, quest_index, completed)
            VALUES (?, ?, 0)
        """, (player_id, quest["id"]))


    con.commit()
    con.close()
    return player_id


def create_session(player_id):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    # Generate a new session token (could use uuid4 for example).
    session_auth = str(uuid.uuid4())
    # SQLite expression datetime('now', '+24 hours') is used in the DEFAULT defined above;
    # however, you can also explicitly set it here if you want:
    expires_at = datetime.datetime.now() + datetime.timedelta(hours=24)
    
    cur.execute("""
        INSERT INTO sessions (player_id, session_auth, created_at, expires_at)
        VALUES (?, ?, datetime('now'), ?)
    """, (player_id, session_auth, expires_at.strftime("%Y-%m-%d %H:%M:%S")))
    con.commit()
    con.close()
    return session_auth

def validate_session(session_auth):
    """Return the associated player_id if session is valid, or None otherwise."""
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("""
        SELECT player_id, expires_at FROM sessions 
        WHERE session_auth = ?
    """, (session_auth,))
    row = cur.fetchone()
    con.close()
    if row:
        expires_at = datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
        if datetime.datetime.now() < expires_at:
            return row[0]
    return None



def get_player_data(player_id, speed=3.5):
    """
    Get all current player data in a dictionary for displaying on screen.
    
    This function reads from the DB without modifying anything. It makes a 
    live ‘projection’ of resource values based on the last update timestamp and
    a dummy rate calculation. (Your game logic might compute rates differently.)
    
    Note: For data to be “up‐to‐date” the update_progress function should be called.
    """
    con = sqlite3.connect(DB_NAME)
    # Use a Row factory so we can refer to fields by name.
    con.row_factory = sqlite3.Row  
    cur = con.cursor()
    
    player_data = {}

    # 1. Get basic player info.
    cur.execute("SELECT player_id, name, last_update FROM players WHERE player_id = ?", (player_id,))
    p_row = cur.fetchone()
    if not p_row:
        con.close()
        return None
    player_data["player_id"] = p_row["player_id"]
    player_data["name"] = p_row["name"]
    player_data["last_update"] = p_row["last_update"]

    # 2. Get Resource values.
    cur.execute("SELECT money, stone, iron, gold, diamond, wood, hay, timestamp FROM resources WHERE player_id = ?", (player_id,))
    res_row = cur.fetchone()
    resources = {}
    if res_row:
        resources["base"] = {
            "money": res_row["money"],
            "stone": res_row["stone"],
            "iron": res_row["iron"],
            "gold": res_row["gold"],
            "diamond": res_row["diamond"],
            "wood": res_row["wood"],
            "hay": res_row["hay"]
        }
        resources["timestamp"] = res_row["timestamp"]
        
        # Calculate time elapsed (without updating DB).
        last_res_time = datetime.datetime.strptime(res_row["timestamp"], "%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now()
        dt_seconds = (now - last_res_time).total_seconds()
        # Apply game speed factor. (Normally update_progress does this then writes new values.)
        effective_hours = (dt_seconds / 3600) * speed
        
        # In your update_progress, you would calculate the income based on your buildings/units.
        # Here we use a dummy income_rate (money per hour) for demonstration.
        income_rate = 10  
        projected_money = res_row["money"] + income_rate * effective_hours
        
        # For the other resources, assume a 0 rate (or add further calculations)
        resources["rate"] = {
            "money": income_rate,
            "stone": 0,
            "iron": 0,
            "gold": 0,
            "diamond": 0,
            "wood": 0,
            "hay": 0
        }
        resources["projected"] = {
            "money": projected_money,
            "stone": res_row["stone"],
            "iron": res_row["iron"],
            "gold": res_row["gold"],
            "diamond": res_row["diamond"],
            "wood": res_row["wood"],
            "hay": res_row["hay"]
        }
    player_data["resources"] = resources

    # 3. Get Buildings info.
    cur.execute("SELECT building_type, level, ongoing_build_progress, timestamp FROM buildings WHERE player_id = ?", (player_id,))
    buildings = []
    for row in cur.fetchall():
        buildings.append({
            "type": row["building_type"],
            "level": row["level"],
            "ongoing_build_progress": row["ongoing_build_progress"],
            "timestamp": row["timestamp"]
        })
    player_data["buildings"] = buildings

    # 4. Get Units info.
    cur.execute("SELECT unit_type, count, level, ongoing_production_progress, queued_count, timestamp FROM units WHERE player_id = ?", (player_id,))
    units = []
    for row in cur.fetchall():
        units.append({
            "type": row["unit_type"],
            "count": row["count"],
            "level": row["level"],
            "ongoing_production_progress": row["ongoing_production_progress"],
            "queued_count": row["queued_count"],
            "timestamp": row["timestamp"]
        })
    player_data["units"] = units

    # 5. Get Trade Offers.
    cur.execute("SELECT id, resources_cost, resources_earned, timestamp FROM trade_offers WHERE player_id = ?", (player_id,))
    offers = []
    for row in cur.fetchall():
        offers.append({
            "id": row["id"],
            "resources_cost": json.loads(row["resources_cost"]),
            "resources_earned": json.loads(row["resources_earned"]),
            "timestamp": row["timestamp"]
        })
    player_data["trade_offers"] = offers

    # 6. Get Quests.
    cur.execute("SELECT quest_index, completed, timestamp FROM quests WHERE player_id = ?", (player_id,))
    quests = []
    for row in cur.fetchall():
        quests.append({
            "quest_index": row["quest_index"],
            "completed": bool(row["completed"]),
            "timestamp": row["timestamp"]
        })
    player_data["quests"] = quests

    # 7. Get any active Production Queue items (not yet completed).
    cur.execute("""
        SELECT id, production_type, entity, start_time, duration, progress, status 
        FROM production_queue 
        WHERE player_id = ? AND status != 'completed'
    """, (player_id,))
    production_rows = []
    for row in cur.fetchall():
        production_rows.append({
            "id": row["id"],
            "production_type": row["production_type"],
            "entity": row["entity"],
            "start_time": row["start_time"],
            "duration": row["duration"],
            "progress": row["progress"],
            "status": row["status"]
        })
    player_data["production_queue"] = production_rows

    con.close()
    return player_data


def update_progress(player_id, speed=3.5):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    
    # Get last_update time from the players table.
    cur.execute("SELECT last_update FROM players WHERE player_id = ?", (player_id,))
    row = cur.fetchone()
    if not row:
        con.close()
        return
    last_update_str = row[0]
    last_update = datetime.datetime.strptime(last_update_str, "%Y-%m-%d %H:%M:%S")
    
    now = datetime.datetime.now()
    dt_seconds = (now - last_update).total_seconds()
    # Calculate effective hours passed (dt in seconds/3600 multiplied by the game speed)
    hours_passed = (dt_seconds / 3600) * speed
    
    # Example: Updating resources (assume you computed an income rate somehow)
    cur.execute("SELECT money FROM resources WHERE player_id = ?", (player_id,))
    money = cur.fetchone()[0]
    # Compute income: For example, your game logic computes income per hour (this is just a placeholder)
    income_rate_per_hour = 10  # change this to your income calculation
    new_money = money + income_rate_per_hour * hours_passed
    cur.execute("UPDATE resources SET money = ?, timestamp = datetime('now') WHERE player_id = ?",
                (int(new_money), player_id))
    
    # Update any ongoing productions in the production_queue.
    # Here we “advance” the progress based on the hours passed and the expected duration.
    cur.execute("""
      SELECT id, production_type, entity, duration, progress
      FROM production_queue 
      WHERE player_id = ? AND status = 'in_progress'
    """, (player_id,))
    for prod_id, prod_type, entity, duration, progress in cur.fetchall():
        # For example, if duration is specified in hours,
        # the fraction of completion is (hours_passed / duration)
        new_progress = progress + (hours_passed / duration)
        if new_progress >= 1:
            new_progress = 1
            # Production complete!
            # Here, update the corresponding player stats (for example, increment building level or unit count)
            if prod_type == "building":
                # Update buildings table: raise level by 1, reset ongoing_build_progress.
                cur.execute("""
                   UPDATE buildings 
                   SET level = level + 1, ongoing_build_progress = NULL, timestamp = datetime('now') 
                   WHERE player_id = ? AND building_type = ?
                """, (player_id, entity))
            elif prod_type == "unit":
                cur.execute("""
                   UPDATE units 
                   SET count = count + 1, ongoing_production_progress = NULL, timestamp = datetime('now')
                   WHERE player_id = ? AND unit_type = ?
                """, (player_id, entity))
            # Mark production as completed:
            cur.execute("UPDATE production_queue SET status = 'completed', progress = ? WHERE id = ?", (new_progress, prod_id))
            
            # Optionally, check for queued production items and start the next one.
            # (This could involve setting status='in_progress', resetting start_time, etc.)
        else:
            # Update progress if still in progress.
            cur.execute("UPDATE production_queue SET progress = ? WHERE id = ?", (new_progress, prod_id))
    
    # Finally update the player’s last_update to now.
    cur.execute("UPDATE players SET last_update = datetime('now') WHERE player_id = ?", (player_id,))
    
    con.commit()
    con.close()



# If run as a script, initialize the DB.
if __name__ == '__main__':
    init_db()
    # To test adding a new player:
    new_player_id = add_new_player("Player 1","password")
    if new_player_id:
        print("Added new player with ID:", new_player_id)
    else:
        print("Player already exists or there was an error.")

    update_progress(new_player_id)
    import time
    time.sleep(2)
    update_progress(new_player_id)



import datetime
import sqlite3

