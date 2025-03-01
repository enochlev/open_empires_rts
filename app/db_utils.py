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
            INSERT INTO buildings (player_id, building_type, level, ongoing_build_progress)
            VALUES (?, ?, ?, NULL)
        """, (player_id, building, game_config["Buildings"][building]["starting_level"]))


    for unit in game_config["Units"].keys():
        if game_config["Units"][unit]["start_amount"] == 0:
            continue
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
def update_progress(player_id, speed=3.5):
    """
    Update resource income and production progress for a given player.
    
    This function does the following:
      • Reads the last_update time for the player and computes effective elapsed hours.
      • Queries the player's buildings and units.
      • Uses the hourly_cost from the game config to update (reduce) resources (money, etc.).
      • Computes the production boost from an existing Church (1.2^level).
      • Looks up any production tasks in production_queue (for Farm, Lumber Mill, Quarry and Mines)
        and adds production progress based on number of workers, building level and multipliers.
      • If enough progress is earned (>=1) the resource is produced; in the case of Mines, a random
        roll determines whether iron, gold or diamond is produced.
      • Finally, both the resources table and production_queue table are updated along with the player's last_update.
    """
    con = sqlite3.connect(DB_NAME)
    # Use a row factory so that rows can be referenced by column name.
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    # 1. Get the last_update timestamp for the player.
    cur.execute("SELECT last_update FROM players WHERE player_id = ?", (player_id,))
    row = cur.fetchone()
    if not row:
        print("No player with id", player_id)
        con.close()
        return
    last_update = datetime.datetime.strptime(row["last_update"], "%Y-%m-%d %H:%M:%S")
    now = datetime.datetime.now()
    dt_seconds = (now - last_update).total_seconds()
    # hours_passed is computed from the elapsed time (in hours) multiplied by your speed factor
    hours_passed = (dt_seconds / 3600) * speed

    # 2. Load multiplier settings from config.
    gs = game_config["game_speed_and_multiplier"]["global_speed"]
    bs = game_config["game_speed_and_multiplier"]["building_speed"]
    us = game_config["game_speed_and_multiplier"]["unit_speed"]
    rs = game_config["game_speed_and_multiplier"]["resource_speed"]
    # We use the building_upgrade_boost_multiplier as our production “base” multiplier (as in your old code)
    prod_multiplier = game_config["game_speed_and_multiplier"]["building_upgrade_boost_multiplier"]
    unit_upgrade_multiplier = game_config["game_speed_and_multiplier"]["unit_upgrade_boost_multiplier"]
    
    # 3. Get the player's buildings and units.
    player_buildings = cur.execute("SELECT * FROM buildings WHERE player_id = ?", (player_id,)).fetchall()
    player_units = cur.execute("SELECT * FROM units WHERE player_id = ?", (player_id,)).fetchall()

    # 4. Compute Church boost (if any, a Church boosts production by 1.2 per level)
    church_level = 0
    for building in player_buildings:
        if building["building_type"] == "Church":
            church_level = building["level"]
            break
    church_multiplier = 1.2 ** church_level

    # 5. Compute income/expense from buildings and units.
    # Initialize a dictionary to accumulate changes.
    resources_added = { "money": 0, "hay": 0, "wood": 0, "stone": 0, "diamond": 0, "gold": 0, "iron": 0 }
    
    # Process building costs/income.
    for building in player_buildings:
        b_type = building["building_type"]
        level = building["level"]
        if b_type in game_config["Buildings"]:
            hourly_cost = game_config["Buildings"][b_type]["hourly_cost"]
            for res, cost in hourly_cost.items():
                # In your old code the building’s money income was updated with:
                #    income += building_level * - hourly_cost
                # So here we subtract (cost × level) and then multiply by the hours passed and multipliers.
                delta = cost * level * hours_passed * gs * bs * church_multiplier
                resources_added[res] -= delta
        else:
            print("Warning: No building config for", b_type)
    
    # Process unit costs/earnings.
    for unit in player_units:
        unit_type = unit["unit_type"]
        count = unit["count"]
        level = unit["level"]
        if unit_type in game_config["Units"]:
            hourly_cost = game_config["Units"][unit_type]["hourly_cost"]
            for res, cost in hourly_cost.items():
                # Note: your new code uses an exponent based on (level - 1).
                delta = (cost ** (level - 1)) * count * hours_passed * gs * us * church_multiplier
                resources_added[res] -= delta
        else:
            print("Warning: No unit config for", unit_type)

    # 6. Process resource production from production_queue.
    # We expect tasks for production_type 'resource' (with entities like "Farm", "Lumber Mill", "Quarry", "Mines").
    production_tasks = cur.execute("""
        SELECT * FROM production_queue 
        WHERE player_id = ? 
          AND production_type = 'resource'
          AND status = 'in_progress'
    """, (player_id,)).fetchall()
    
    # For each production task, add production progress.
    for task in production_tasks:
        entity = task["entity"]  # For example "Farm", "Lumber Mill", etc.
        workers = task["number_of_workers"]
        current_progress = task["progress"]
        # Get the building level for the corresponding entity.
        building_level = None
        for b in player_buildings:
            if b["building_type"] == entity:
                building_level = b["level"]
                break
        if (building_level is None) or (building_level == 0):
            # No valid building; skip production for this task.
            continue
        
        # Production rate follows a formula similar to your old code:
        # progress += (prod_multiplier^(building_level - 1)) * workers * hours_passed * church_multiplier
        # In addition, we multiply by the global and resource speed multipliers.
        production_rate = (prod_multiplier ** (building_level - 1)) * workers * hours_passed * gs * rs * church_multiplier
        
        new_progress = current_progress + production_rate
        whole_units = int(new_progress)  # whole production units that were reached
        remainder = new_progress - whole_units
        
        # For each resource-producing building adjust the appropriate resource.
        if entity == "Farm":
            # Farm produces hay (whole unit means 1 hay)
            resources_added["hay"] += whole_units
        elif entity == "Lumber Mill":
            # Lumber Mill produces wood
            resources_added["wood"] += whole_units
        elif entity == "Quarry":
            # Quarry produces stone
            resources_added["stone"] += whole_units
        elif entity == "Mines":
            # For each whole unit produced by a mine, roll to decide what is produced.
            # (If roll <= 5: diamond, elif roll <= 20: gold; otherwise iron.)
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
        
        # Update the production task’s progress (keep the fractional remainder)
        cur.execute("UPDATE production_queue SET progress = ? WHERE id = ?", (remainder, task["id"]))

    # 7. Update the player's resources.
    # Here we loop through the keys we expect and update using a separate query.
    for res, amount in resources_added.items():
        # Using string formatting for column names is safe here because these keys are predefined.
        cur.execute("UPDATE resources SET {} = {} + ? WHERE player_id = ?".format(res, res), (amount, player_id))
    
    # 8. Overwrite last_update to now.
    cur.execute("UPDATE players SET last_update = ? WHERE player_id = ?", (now.strftime("%Y-%m-%d %H:%M:%S"), player_id))
    
    con.commit()
    con.close()


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

