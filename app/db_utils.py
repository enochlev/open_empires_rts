import sqlite3
import datetime
import json
import uuid
import random

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
        default_value = str(int(game_config["Resources"][resource]["default"]))
        resource_string += f"{resource} FLOAT DEFAULT {default_value}, "
    resource_string = resource_string[:-2]

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS resources (
            resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            {resource_string},
            FOREIGN KEY(player_id) REFERENCES players(player_id)
        );
    """)
    #if table exists make sure all resources are in the table
    #if not add them with default values
    #if extra resources are in the table, remove them

    cur.execute(f"SELECT * FROM resources")
    columns = [description[0] for description in cur.description]
    for resource in all_resources:
        if resource not in columns:
            cur.execute(f"ALTER TABLE resources ADD COLUMN {resource} FLOAT DEFAULT {game_config['Resources'][resource]['default']}")
    for column in columns:
        if column not in list(all_resources) + ["resource_id", "player_id", "timestamp"]:
            cur.execute(f"ALTER TABLE resources DROP COLUMN {column}")
    
    # A table for player buildings. For each building you can store:
    # level, any ongoing build progress (a float between 0 and 1) and a timestamp.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS buildings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            building_type TEXT,
            level INTEGER DEFAULT 0,
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
            production_type TEXT,      -- 'building' or 'unit' or 'resource' or 'research'
            entity TEXT,               -- which building (e.g., 'Barracks') or unit (e.g., 'Soldier') or resource (e.g., 'money')
            number_of_workers INTEGER, -- number of workers assigned to the task
            start_time TIMESTAMP DEFAULT (datetime('now')),
            duration REAL,             -- expected duration (in seconds, or hours) needed to complete
            progress REAL DEFAULT 0,     -- a float tracking current progress between 0 and 1
            status TEXT DEFAULT 'in_progress',  -- could be in_progress, or queued
            FOREIGN KEY(player_id) REFERENCES players(player_id)
        );
    """)
    
    con.commit()
    con.close()




def add_new_player(name, plain_password):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    
    password_hash = generate_password_hash(plain_password)
    del plain_password  # Remove the plain password from memory.

    #assert player username does not exist
    cur.execute("SELECT player_id FROM players WHERE name = ?", (name,))
    row = cur.fetchone()
    if row:
        con.close()
        return row[0]
        #return player_id
    
    cur.execute("""
        INSERT OR IGNORE INTO players (name, password_hash, last_update)
        VALUES (?, ?, ?)
    """, (name, password_hash, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
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
        value_string += f"{game_config['Resources'][resource]['default']}, "
    resource_string = resource_string[:-2]
    value_string = value_string[:-2]
    
    cur.execute(f"""
        INSERT INTO resources (player_id, {resource_string})
        VALUES (?, {value_string})
    """, (player_id,))

    

    for building in game_config["Buildings"].keys():
        if game_config["Buildings"][building]["starting_level"] == 0:
            continue
        
        cur.execute("""
            INSERT INTO buildings (player_id, building_type, level)
            VALUES (?, ?, ?)
        """, (player_id, building, game_config["Buildings"][building]["starting_level"]))


    for unit in game_config["Units"].keys():
        if game_config["Units"][unit]["start_amount"] == 0:
            continue
        cur.execute("""
            INSERT INTO units (player_id, unit_type, count, level)
            VALUES (?, ?, ?, ?)
        """, (player_id, unit, game_config["Units"][unit]["start_amount"], game_config["Units"][unit]["starting_level"]))
    

    for quest in game_config["Quests"]:
        cur.execute("""
            INSERT INTO quests (player_id, quest_index, completed)
            VALUES (?, ?, 0)
        """, (player_id, quest["id"]))


    con.commit()
    con.close()
    return player_id


def create_session(player_id, plain_password):

    hashed_password = generate_password_hash(plain_password)
    del plain_password  # Remove the plain password from memory.


    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()


    # Check if the player exists and the password matches.
    cur.execute("SELECT player_id FROM players WHERE player_id = ? AND password_hash = ?", (player_id, hashed_password))
    row = cur.fetchone()
    if not row:
        con.close()
        return None

    # Generate a new session token (could use uuid4 for example).
    session_auth = str(uuid.uuid4())
    # SQLite expression datetime('now', '+24 hours') is used in the DEFAULT defined above;
    # however, you can also explicitly set it here if you want:
    now = datetime.datetime.now()
    expires_at = now + datetime.timedelta(hours=24)
    
    cur.execute("""
        INSERT INTO sessions (player_id, session_auth, created_at, expires_at)
        VALUES (?, ?, ?, ?)
    """, (player_id, session_auth, now.strftime("%Y-%m-%d %H:%M:%S"), expires_at.strftime("%Y-%m-%d %H:%M:%S")))
    con.commit()
    con.close()
    return session_auth

def validate_session(player_id, session_auth):
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
        assert row[0] == player_id, "Player ID does not match session."

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


def update_unit_production(player_id, hours_passed, con):
    """
    Process production_queue entries of type 'unit_production'.
    In these tasks the entity field is in the format "Building.Unit" (for example "Stables.Calvary").
    We group tasks by the production building first (so that production is affected by that building’s level)
    and then by unit type.
    
    For each queued task we:
      • Look up the unit config (using game_config["Units"]).
      • Calculate a rate based on:
             rate = (1 / hours_to_build)
                    × smithy_boost           (from player's Smithy level)
                    × (unit_upgrade_multiplier^(production_building_level - 1))
      • Increment the task’s progress by: progress += hours_passed * rate.
      • If progress ≥ 1 then complete that task (update the unit count and remove the queue row).
      • Otherwise update progress and compute an expected finish time.
      
    Returns a list of datetime objects for the next expected completion times.
    """
    cur = con.cursor()
    # Get all queued unit production tasks.
    prod_tasks = cur.execute("""
        SELECT *
          FROM production_queue
         WHERE player_id = ?
           AND production_type = 'unit_production'
         ORDER BY start_time
    """, (player_id,)).fetchall()
    
    # Group tasks by production building and then by unit type.
    # Instead of using defaultdict – we do this manually.
    groups = {}
    for task in prod_tasks:
        # We expect the entity to be in the form "Building.Unit", e.g., "Stables.Calvary".
        parts = task["entity"].split('.')
        if len(parts) != 2:
            print("Invalid entity format in unit production task:", task["entity"])
            continue
        prod_building, unit_type = parts
        if prod_building not in groups:
            groups[prod_building] = {}
        if unit_type not in groups[prod_building]:
            groups[prod_building][unit_type] = []
        groups[prod_building][unit_type].append(task)
    
    # Fetch the player’s buildings (to get levels for production buildings and Smithy).
    buildings = cur.execute("SELECT * FROM buildings WHERE player_id = ?", (player_id,)).fetchall()
    building_levels = {b["building_type"]: b["level"] for b in buildings}
    
    # Smithy always affects unit production – get its level and compute boost.
    smithy_level = building_levels.get("Smithy", 0)
    smithy_boost = 1.2 ** smithy_level
    unit_upgrade_multiplier = game_config["game_speed_and_multiplier"]["unit_upgrade_boost_multiplier"]
    
    expected_timestamps = []
    now = datetime.datetime.now()
    
    # Process each production building group.
    for prod_building in groups:
        # The production building level affects the rate.
        current_building_level = building_levels.get(prod_building, 0)
        if current_building_level == 0:
            # If the production building isn’t available, skip these tasks.
            continue
        for unit_type in groups[prod_building]:
            # Make sure this unit exists in the game config.
            if unit_type not in game_config["Units"].keys():
                print("Warning: Unit config not found for", unit_type)
                continue
            unit_config = game_config["Units"][unit_type]
            hours_to_build = unit_config["hours_to_build"]
            # Compute the production rate for this unit:
            # rate (units per hour) = (1 / hours_to_build)
            #                           × smithy_boost
            #                           × (unit_upgrade_multiplier^(current_building_level - 1))
            rate = (1.0 / hours_to_build) * smithy_boost * (unit_upgrade_multiplier ** (current_building_level - 1))
            
            # Sort tasks (by start_time) for this production building/unit group.
            tasks_list = sorted(groups[prod_building][unit_type], key=lambda x: x["start_time"])
            for task in tasks_list:
                prog = task["progress"]
                new_prog = prog + hours_passed * rate
                if new_prog >= 1:
                    # Complete the production: add one unit to the player's count.
                    cur.execute("""
                        UPDATE units 
                           SET count = count + 1 
                         WHERE player_id = ? AND unit_type = ?
                    """, (player_id, unit_type))
                    # Remove the completed production task.
                    cur.execute("DELETE FROM production_queue WHERE id = ?", (task["id"],))
                    # (If you wish, you can check leftover progress and immediately process the next task.)
                else:
                    # Still in progress – update the task’s progress.
                    cur.execute("UPDATE production_queue SET progress = ? WHERE id = ?", (new_prog, task["id"]))
                    remaining = 1 - new_prog
                    expected_hours = remaining / rate if rate > 0 else float('inf')
                    expected_timestamps.append(now + datetime.timedelta(hours=expected_hours))
                    # Only process the first incomplete task for this unit type.
                    break
    return expected_timestamps

def update_unit_research(player_id, hours_passed, con):
    """
    Process production_queue entries of type 'unit_research'. These tasks are assumed
    to be for upgrading a unit (i.e. “research”) and are affected only by Smithy level and global speed.
    The entity field in these tasks is assumed to be just the unit name.
    
    For each research task we:
      • Look up the unit config (using game_config["Units"]).
      • Determine the research time (using unit_config["hours_to_research"] if available,
        or defaulting to unit_config["hours_to_build"]).
      • Compute a rate:
             rate = (1 / hours_to_research)
                    × smithy_boost    (from player’s Smithy level)
                    × global_speed  (from game_config multiplier)
      • Update progress by: progress += hours_passed * rate.
      • If progress ≥ 1 then complete this research (for example, increment the unit’s level)
        and remove the queue row.
      • Otherwise update progress and compute an expected finish timestamp.
    
    Returns a list of expected completion timestamps.
    """
    cur = con.cursor()
    research_tasks = cur.execute("""
       SELECT *
         FROM production_queue
        WHERE player_id = ?
          AND production_type = 'unit_research'
        ORDER BY start_time
    """, (player_id,)).fetchall()
    
    # Get the Smithy level from the player's buildings.
    buildings = cur.execute("SELECT * FROM buildings WHERE player_id = ?", (player_id,)).fetchall()
    building_levels = {b["building_type"]: b["level"] for b in buildings}
    smithy_level = building_levels.get("Smithy", 0)
    smithy_boost = 1.2 ** smithy_level
    
    gs = game_config["game_speed_and_multiplier"]["global_speed"]
    
    expected_timestamps = []
    now = datetime.datetime.now()
    
    for task in research_tasks:
        # For research, we assume entity is just the unit name.
        unit_type = task["entity"]
        if unit_type not in game_config["Units"].keys():
            print("Warning: Unit config not found for research unit", unit_type)
            continue
        unit_config = game_config["Units"][unit_type]
        # Use a research-specific time if provided; if not, default to hours_to_build.
        hours_to_research = unit_config.get("hours_to_research", unit_config["hours_to_build"])
        # Compute research rate: note that only Smithy and global speed affect research.
        rate = (1.0 / hours_to_research) * smithy_boost * gs
        
        prog = task["progress"]
        new_prog = prog + hours_passed * rate
        if new_prog >= 1:
            # Research is complete – update the unit’s research upgrade,
            # for example by incrementing its level.
            cur.execute("""
                UPDATE units 
                   SET level = level + 1 
                 WHERE player_id = ? AND unit_type = ?
            """, (player_id, unit_type))
            cur.execute("DELETE FROM production_queue WHERE id = ?", (task["id"],))
        else:
            cur.execute("UPDATE production_queue SET progress = ? WHERE id = ?", (new_prog, task["id"]))
            remaining = 1 - new_prog
            expected_hours = remaining / rate if rate > 0 else float('inf')
            expected_timestamps.append(now + datetime.timedelta(hours=expected_hours))
            # Only process one in-progress research task per unit.
    return expected_timestamps

def update_units(player_id, hours_passed, con):
    """
    Master update routine for units. This calls both the unit production and the 
    unit research update functions and returns a list of expected completion timestamps.
    These timestamps can then be used (for example) to inform when the next unit 
    or research upgrade will complete.
    """
    production_times = update_unit_production(player_id, hours_passed, con)
    research_times = update_unit_research(player_id, hours_passed, con)
    return production_times + research_times

# ----------------------------------------------------------------
def update_buildings(player_id, hours_passed, con):
    """
    Process production_queue entries of type "building".
    
    For each building production task:
      • Look up the building’s hours to build.
      • Production progress is incremented by:
            progress += (number_of_workers * global_speed * building_speed * hours_passed) 
                          / (hours_to_build * (upgrade_multiplier ** (current_level - 1)))
      • If progress >= 1 then the building upgrade is complete and we increment 
        the player’s building level (and remove the queue item). (Extra progress
        could be cascaded onto the next queued item if you wish.)
      • For an incomplete task we compute an expected completion timestamp.
    """
    cur = con.cursor()
    # Get player buildings so we know current levels.
    buildings = cur.execute("SELECT * FROM buildings WHERE player_id = ?", (player_id,)).fetchall()
    building_levels = {b["building_type"]: b["level"] for b in buildings}
    
    expected_timestamps = []
    now = datetime.datetime.now()

    # Get production tasks of type building.
    bld_queue = cur.execute("""
        SELECT *
          FROM production_queue 
         WHERE player_id = ? 
           AND production_type = 'building'
         ORDER BY start_time
    """, (player_id,)).fetchall()

    for item in bld_queue:
        bld_type = item["entity"]
        curr_level = building_levels.get(bld_type, 0)
        if curr_level == 0:
            # Skip if the building is not yet built.
            continue
        if bld_type not in game_config["Buildings"]:
            print("Warning: No building config for", bld_type)
            continue

        hours_to_build = game_config["Buildings"][bld_type]["hours_to_build"]
        workers = item["number_of_workers"]
        upgrade_multiplier = game_config["game_speed_and_multiplier"]["building_upgrade_boost_multiplier"]
        gs = game_config["game_speed_and_multiplier"]["global_speed"]
        bs = game_config["game_speed_and_multiplier"]["building_speed"]

        # Calculate production rate for building upgrades (per hour).
        rate = workers * gs * bs / (hours_to_build * (upgrade_multiplier ** (curr_level - 1)))
        prog = item["progress"]
        new_prog = prog + hours_passed * rate
        if new_prog >= 1:
            # Complete the building production: increase level.
            cur.execute("""
                UPDATE buildings 
                   SET level = level + 1 
                 WHERE player_id = ? AND building_type = ?
            """, (player_id, bld_type))
            cur.execute("DELETE FROM production_queue WHERE id = ?", (item["id"],))
            # (Extra progress could be passed on to next queued production if you wish.)
        else:
            cur.execute("UPDATE production_queue SET progress = ? WHERE id = ?", (new_prog, item["id"]))
            remaining = 1 - new_prog
            expected_hours = remaining / rate if rate > 0 else float('inf')
            expected_timestamps.append(now + datetime.timedelta(hours=expected_hours))
            # Process only one in‐progress building task per type for now.
    return expected_timestamps

# ----------------------------------------------------------------
def update_resources(player_id, hours_passed, con):
    """
    Update the player's resources. In this step:
      • Buildings and units subtract (or add) resources (using configured hourly_costs).
      • Production tasks of type "resource"—which represent infinite production (e.g., a Farm producing hay)
        —have their progress incremented.
      • The corresponding resource is produced when the production progress reaches one whole unit,
        and only the fractional remainder is retained.
      • Finally, update the player's last_update timestamp.
    """
    cur = con.cursor()
    now = datetime.datetime.now()

    # Get player's buildings and units.
    player_buildings = cur.execute("SELECT * FROM buildings WHERE player_id = ?", (player_id,)).fetchall()
    player_units = cur.execute("SELECT * FROM units WHERE player_id = ?", (player_id,)).fetchall()

    # Compute church boost (if any).
    church_level = 0
    for b in player_buildings:
        if b["building_type"] == "Church":
            church_level = b["level"]
            break
    church_multiplier = 1.2 ** church_level

    # Initialize resource delta dictionary.
    resources_added = {res: 0 for res in game_config["Resources"]}

    gs = game_config["game_speed_and_multiplier"]["global_speed"]
    bs = game_config["game_speed_and_multiplier"]["building_speed"]
    us = game_config["game_speed_and_multiplier"]["unit_speed"]
    rs = game_config["game_speed_and_multiplier"]["resource_speed"]

    # Process building income/expenses.
    for b in player_buildings:
        b_type = b["building_type"]
        lvl = b["level"]
        if b_type in game_config["Buildings"]:
            hourly_cost = game_config["Buildings"][b_type]["hourly_cost"]
            for res, cost in hourly_cost.items():
                delta = cost * lvl * hours_passed * gs * bs * church_multiplier
                resources_added[res] -= delta
        else:
            print("Warning: No building config for", b_type)

    # Process unit income/expenses.
    for unit in player_units:
        unit_type = unit["unit_type"]
        count = unit["count"]
        lvl = unit["level"]
        if unit_type in game_config["Units"]:
            hourly_cost = game_config["Units"][unit_type]["hourly_cost"]
            for res, cost in hourly_cost.items():
                # Note: using exponent (lvl - 1) as in your old code.
                delta = (cost ** (lvl - 1)) * count * hours_passed * gs * us * church_multiplier
                resources_added[res] -= delta
        else:
            print("Warning: No unit config for", unit_type)

    # Process production tasks of type "resource"
    resource_queue = cur.execute("""
        SELECT *
          FROM production_queue 
         WHERE player_id = ?
           AND production_type = 'resource'
           AND status = 'in_progress'
    """, (player_id,)).fetchall()
    # For resource production, we “never” remove the queue item.
    prod_multiplier = game_config["game_speed_and_multiplier"]["building_upgrade_boost_multiplier"]
    for item in resource_queue:
        entity = item["entity"]  # e.g., "Farm", "Lumber Mill", etc.
        workers = item["number_of_workers"]
        curr_prog = item["progress"]
        # Find the corresponding building level (skip if not found).
        bld_level = None
        for b in player_buildings:
            if b["building_type"] == entity:
                bld_level = b["level"]
                break
        if (bld_level is None) or (bld_level == 0):
            continue

        rate = (prod_multiplier ** (bld_level - 1)) * workers * hours_passed * gs * rs * church_multiplier
        new_prog = curr_prog + rate
        whole_units = int(new_prog)
        remainder = new_prog - whole_units

        if entity == "Farm":
            resources_added["hay"] += whole_units
        elif entity == "Lumber Mill":
            resources_added["wood"] += whole_units
        elif entity == "Quarry":
            resources_added["stone"] += whole_units
        elif entity == "Mines":
            for _ in range(whole_units):
                roll = random.randint(1, 100)
                if roll <= 5:
                    resources_added["diamond"] += 1
                elif roll <= 20:
                    resources_added["gold"] += 1
                else:
                    resources_added["iron"] += 1
        else:
            print("Warning: Unknown production entity", entity)
        
        cur.execute("UPDATE production_queue SET progress = ? WHERE id = ?", (remainder, item["id"]))

    # Update the player's resources.
    for res, delta in resources_added.items():
        # Safe to use string formatting for column names because your resource names are known.
        cur.execute("UPDATE resources SET {} = {} + ? WHERE player_id = ?".format(res, res), (delta, player_id))

    # Update player's last_update timestamp.
    cur.execute("UPDATE players SET last_update = ? WHERE player_id = ?", (now.strftime("%Y-%m-%d %H:%M:%S"), player_id))

    # No expected timestamps are returned from resource update.
    return

def update_progress(player_id):
    """
    Example update_progress routine that calls update_units (as well as other update functions).
    """
    con = sqlite3.connect(DB_NAME)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    cur.execute("SELECT last_update FROM players WHERE player_id = ?", (player_id,))
    row = cur.fetchone()
    if not row:
        print("No player with id", player_id)
        con.close()
        return

    last_update = datetime.datetime.strptime(row["last_update"], "%Y-%m-%d %H:%M:%S")
    now = datetime.datetime.now()
    dt_seconds = (now - last_update).total_seconds()
    hours_passed = dt_seconds / 3600.0

    # Update units (production and research)
    unit_timestamps = update_units(player_id, hours_passed, con)
    
    # ... you could call update_buildings(player_id, hours_passed, con) and update_resources(player_id, hours_passed, con) here
    update_resources(player_id, hours_passed, con)
    update_units(player_id, hours_passed, con)
    update_buildings(player_id, hours_passed, con)

    # Update the player's last_update time.
    cur.execute("UPDATE players SET last_update = ? WHERE player_id = ?", (now.strftime("%Y-%m-%d %H:%M:%S"), player_id))
    
    con.commit()
    con.close()
    
    return unit_timestamps


def create_dataframes():
    import pandas as pd

    con = sqlite3.connect(DB_NAME)

    df_players = pd.read_sql_query("SELECT * FROM players", con)
    df_resources = pd.read_sql_query("SELECT * FROM resources", con)
    df_buildings = pd.read_sql_query("SELECT * FROM buildings", con)
    df_units = pd.read_sql_query("SELECT * FROM units", con)
    df_trade_offers = pd.read_sql_query("SELECT * FROM trade_offers", con)
    df_quests = pd.read_sql_query("SELECT * FROM quests", con)
    df_production_queue = pd.read_sql_query("SELECT * FROM production_queue", con)

    con.close()
    return {"players": df_players, "resources": df_resources, "buildings": df_buildings, "units": df_units, "trade_offers": df_trade_offers, "quests": df_quests, "production_queue": df_production_queue}


# If run as a script, initialize the DB.
if __name__ == '__main__':
    init_db()
    # To test adding a new player:
    new_player_id = add_new_player("Player 1","password")
    session_id = create_session(new_player_id, "password")
    
    session_valid = validate_session(new_player_id, session_id)
    if session_valid == None:
        print("Session not valid")

    #create_dataframes()

    update_progress(new_player_id)
    import time
    time.sleep(2)
    update_progress(new_player_id)



import datetime
import sqlite3

