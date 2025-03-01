import sqlite3
import datetime
import json
import uuid
import random

game_config = {}
with open("default_game_config.json") as f:
    game_config = json.load(f)


class PlayerAPI:
    def __init__(self, player_id):
        self.player_id = player_id
        # Here we assume that you already have a loaded dictionary of player_stats.
        # For example, you might load it from the DB when the player logs in.
        self.player_stats = self.load_player_stats()
        # Also open a connection to the DB
        self.db = sqlite3.connect(DB_NAME)
        self.db.row_factory = sqlite3.Row


    def load_player_stats(self):
        stats = {}

        # ----------------------
        # Initialize Buildings
        stats["Buildings"] = {}
        stats["Buildings"]["levels"] = {}
        stats["Buildings"]["assigned_workers"] = {}
        stats["Buildings"]["ongoing_builds"] = {}
        stats["Buildings"]["queued_builds"] = {}
        for building, conf in game_config["Buildings"].items():
            default_level = conf.get("default_level", 0)
            # Ensure there is at least a level 1 Castle:
            if building == "Castle" and default_level == 0:
                default_level = 1
            stats["Buildings"]["levels"][building] = default_level

            # For worker-assigned buildings we could default to zero.
            stats["Buildings"]["assigned_workers"][building] = 0

            # No build in progress initially.
            stats["Buildings"]["ongoing_builds"][building] = None

            # Queued tasks start with zero.
            stats["Buildings"]["queued_builds"][building] = 0

        # ----------------------
        # Initialize Units
        stats["Units"] = {}
        stats["Units"]["levels"] = {}
        stats["Units"]["count"] = {}
        stats["Units"]["ongoing_builds"] = {}
        stats["Units"]["queued_builds"] = {}
        stats["Units"]["ongoing_upgrades"] = {}
        stats["Units"]["queued_upgrades"] = {}
        for unit, conf in game_config["Units"].items():
            default_level = conf.get("default_level", 0)
            if unit == "Citizen" and default_level == 0:
                default_level = 1
            stats["Units"]["levels"][unit] = default_level

            default_count = conf.get("default_count", 0)
            if unit == "Citizen" and default_count == 0:
                default_count = 10
            stats["Units"]["count"][unit] = default_count

            # No unit production or upgrade in progress at player creation.
            stats["Units"]["ongoing_builds"][unit] = None
            stats["Units"]["queued_builds"][unit] = 0
            stats["Units"]["ongoing_upgrades"][unit] = None
            stats["Units"]["queued_upgrades"][unit] = 0

        # ----------------------
        # Initialize Resources
        stats["Resources"] = {}
        for resource, conf in game_config["Resources"].items():
            stats["Resources"][resource] = conf.get("default", 0)

        # ----------------------
        # Load Quests from DB
        # Here we assume that game_config may contain a list of quest templates.
        # The quests table stores for each player:
        #    quest_index (that corresponds to the quest id from game_config)
        #    and a completed flag.
        stats["Quests"] = []
        cur = self.db.cursor()
        cur.execute("SELECT quest_index, completed, timestamp FROM quests WHERE player_id = ?", (self.player_id,))
        quest_rows = cur.fetchall()
        # Assuming game_config["Quests"] is a list of quest templates (dictionaries)
        quest_templates = game_config.get("Quests", [])
        for row in quest_rows:
            # Find the matching quest template if it exists.
            matching = next((q for q in quest_templates if q["id"] == row["quest_index"]), None)
            if matching:
                quest = matching.copy()
            else:
                # Use a minimal structure if no matching template is found.
                quest = {"id": row["quest_index"]}
            quest["completed"] = bool(row["completed"])
            quest["timestamp"] = row["timestamp"]
            stats["Quests"].append(quest)

        # ----------------------
        # Load Trades from DB
        # In this example we load all trade offers.
        # Depending on your game logic you might want to adjust the SQL (for example, showing only trades not created by the current player).
        stats["Trades"] = []
        cur.execute("SELECT id, player_id, resources_cost, resources_earned, timestamp FROM trade_offers")
        trade_rows = cur.fetchall()
        for row in trade_rows:
            try:
                resources_cost = json.loads(row["resources_cost"])
            except Exception:
                resources_cost = {}
            try:
                resources_earned = json.loads(row["resources_earned"])
            except Exception:
                resources_earned = {}

            trade = {
                "id": row["id"],
                "resources_cost": resources_cost,
                "resources_earned": resources_earned,
                # In the game_config sample the key 'source_player' was expected.
                # Here we simply return the player_id of the trade creator.
                "source_player": row["player_id"],
                "timestamp": row["timestamp"]
            }
            stats["Trades"].append(trade)

        return stats


    def check_if_player_has_enough_resources(self, resources_dict):
        # resources_dict is something like {"money": 100, "stone": 10, ...}
        for resource, needed in resources_dict.items():
            if self.player_stats["Resources"].get(resource, 0) < needed:
                return False
        return True

    def purchase_unit(self, unit_type):
        # Validate unit type exists in our config.
        if unit_type not in game_config["Units"]:
            return "Not a valid unit type"
        
        # Check that the building required to produce the unit is built.
        building_source = game_config["Units"][unit_type]["building_source"]
        if self.player_stats["Buildings"]["levels"].get(building_source, 0) == 0:
            return f"{building_source} must be built first"
        
        # Check that the unit itself has been unlocked (level > 0).
        unit_level = self.player_stats["Units"]["levels"].get(unit_type, 0)
        if unit_level == 0:
            return "Unit level is 0, please unlock by upgrading in Smithy"
        
        # For Citizen, make sure the village capacity is not exceeded.
        if unit_type == "Citizen":
            current_producing = 1 if self.player_stats["Units"]["ongoing_builds"].get(unit_type) is not None else 0
            in_queue = self.player_stats["Units"]["queued_builds"].get(unit_type, 0)
            current_count = self.player_stats["Units"]["count"].get(unit_type, 0)
            village_house_level = self.player_stats["Buildings"]["levels"].get("Village House", 0)
            if current_producing + in_queue + current_count >= village_house_level * 5:
                return "Please Upgrade Village House"
        
        # Calculate unit cost (apply cost multiplier depending on the unit level).
        unit_cost = copy.deepcopy(game_config["Units"][unit_type]["cost"])
        for resource, cost in unit_cost.items():
            unit_cost[resource] = cost * (upgrade_multiplier ** (unit_level - 1))
        
        # Check if enough resources are available.
        if not self.check_if_player_has_enough_resources(unit_cost):
            return "Not Enough Resources"
        
        # Deduct resources.
        for resource, cost in unit_cost.items():
            self.player_stats["Resources"][resource] -= cost
        
        # For a unit build, the production queue row uses production_type "unit_production"
        # and the entity is built as "<production_building>.<unit_type>" (e.g., "Stables.Calvary").
        # In unit production you only assign one worker per task.
        entity = building_source + '.' + unit_type
        
        # Insert a new row in the production_queue table.
        cur = self.db.cursor()
        cur.execute("""
            INSERT INTO production_queue (player_id, production_type, entity, number_of_workers, progress, status)
            VALUES (?, 'unit_production', ?, 1, 0.0, 'in_progress')
        """, (self.player_id, entity))
        self.db.commit()
        
        # Update the in-memory queue counter.
        self.player_stats["Units"]["queued_builds"][unit_type] += 1
        return "Success"
    
    def remove_unit_from_queue(self, unit_type):
        if unit_type not in game_config["Units"]:
            return "Not a valid unit type"

        queued = self.player_stats["Units"]["queued_builds"].get(unit_type, 0)
        ongoing = self.player_stats["Units"]["ongoing_builds"].get(unit_type)
        if queued == 0 and ongoing is None:
            return "No units in queue"
        
        cur = self.db.cursor()
        # For unit production there is only one worker per queue row.
        if queued > 0:
            # Remove one queued item (we assume a row with progress==0 means not yet started).
            cur.execute("""
                DELETE FROM production_queue
                WHERE player_id = ? AND production_type = 'unit_production'
                  AND entity = ? AND progress = 0
                LIMIT 1
            """, (self.player_id, game_config["Units"][unit_type]["building_source"] + '.' + unit_type))
            self.player_stats["Units"]["queued_builds"][unit_type] -= 1
        elif ongoing is not None:
            # If a production is in progress, cancel it (set to cancelled).
            cur.execute("""
                UPDATE production_queue
                SET progress = 0, status = 'cancelled'
                WHERE player_id = ? AND production_type = 'unit_production'
                  AND entity = ?
                LIMIT 1
            """, (self.player_id, game_config["Units"][unit_type]["building_source"] + '.' + unit_type))
            self.player_stats["Units"]["ongoing_builds"][unit_type] = None

        # Refund the unit cost.
        unit_level = self.player_stats["Units"]["levels"].get(unit_type, 0)
        unit_cost = copy.deepcopy(game_config["Units"][unit_type]["cost"])
        for resource, cost in unit_cost.items():
            unit_cost[resource] = cost * (upgrade_multiplier ** (unit_level - 1))
            self.player_stats["Resources"][resource] += unit_cost[resource]
        self.db.commit()
        return "Success"
    
    def purchase_building(self, building_type):
        # First check for an available worker.
        if self.number_of_available_workers() <= 0:
            return "Not Enough Workers available"
        
        if building_type not in game_config["Buildings"]:
            return "Not a valid building type"
        
        current_level = self.player_stats["Buildings"]["levels"].get(building_type, 0)
        if current_level == game_config["Buildings"][building_type]["max"]:
            return "Max Level Reached"
        
        if self.player_stats["Buildings"]["ongoing_builds"].get(building_type) is not None:
            return "Already Upgrading"
        
        # Check whether overall number of buildings meets the castle limit.
        ongoing_building_upgrades = sum(1 for val in self.player_stats["Buildings"]["ongoing_builds"].values() if val is not None)
        number_of_buildings = sum(self.player_stats["Buildings"]["levels"].values())
        if building_type != "Castle" and number_of_buildings + ongoing_building_upgrades >= self.player_stats["Buildings"]["levels"].get("Castle", 0) * 5:
            return "Not Enough Castle Level"
        
        # Calculate building cost. (Multiply cost by cost multiplier raised to current_level.)
        building_cost = copy.deepcopy(game_config["Buildings"][building_type]["cost"])
        for resource, cost in building_cost.items():
            building_cost[resource] = cost * (upgrade_multiplier ** current_level)
        
        if not self.check_if_player_has_enough_resources(building_cost):
            return "Not Enough Resources"
        
        # Deduct building cost.
        for resource, cost in building_cost.items():
            self.player_stats["Resources"][resource] -= cost
        
        # Insert a construction task in the production_queue.
        cur = self.db.cursor()
        cur.execute("""
            INSERT INTO production_queue (player_id, production_type, entity, number_of_workers, progress, status)
            VALUES (?, 'construction', ?, 1, 0.0, 'in_progress')
        """, (self.player_id, building_type))
        self.db.commit()
        
        # Mark the building as “in progress” in your in‐memory stats.
        self.player_stats["Buildings"]["ongoing_builds"][building_type] = 0.0
        return "Success"
    
    def upgrade_unit(self, unit_type):
        # Require that the Smithy is built.
        if self.player_stats["Buildings"]["levels"].get("Smithy", 0) == 0:
            return "Smithy must be built first"
        
        # Check none of the unit upgrades are already in progress.
        for ut, prog in self.player_stats["Units"]["ongoing_upgrades"].items():
            if prog is not None:
                return "Already Upgrading"
        
        if unit_type not in game_config["Units"]:
            return "Not a valid unit type"
        
        if self.player_stats["Units"]["levels"].get(unit_type, 0) == game_config["Units"][unit_type]["max"]:
            return "Max Level Reached"
        
        # Calculate upgrade (research) cost.
        unit_cost = copy.deepcopy(game_config["Units"][unit_type]["upgrade_cost"])
        unit_level = self.player_stats["Units"]["levels"].get(unit_type, 0)
        for resource, cost in unit_cost.items():
            unit_cost[resource] = cost * (upgrade_multiplier ** unit_level)
        
        if not self.check_if_player_has_enough_resources(unit_cost):
            return "Not Enough Resources"
        
        # Deduct the cost.
        for resource, cost in unit_cost.items():
            self.player_stats["Resources"][resource] -= cost
        
        # Insert an upgrade (research) task into the production_queue.
        cur = self.db.cursor()
        cur.execute("""
            INSERT INTO production_queue (player_id, production_type, entity, number_of_workers, progress, status)
            VALUES (?, 'unit_research', ?, 1, 0.0, 'in_progress')
        """, (self.player_id, unit_type))
        self.db.commit()
        
        self.player_stats["Units"]["ongoing_upgrades"][unit_type] = 0.0
        return "Success"
    
    def number_of_available_workers(self):
        # Calculate available citizens after subtracting those already assigned.
        resource_collectors = (
            self.player_stats["Buildings"]["assigned_workers"].get("Farm", 0) +
            self.player_stats["Buildings"]["assigned_workers"].get("Quarry", 0) +
            self.player_stats["Buildings"]["assigned_workers"].get("Lumber Mill", 0) +
            self.player_stats["Buildings"]["assigned_workers"].get("Mines", 0)
        )
        construction_workers = sum(1 for val in self.player_stats["Buildings"]["ongoing_builds"].values() if val is not None)
        return self.player_stats["Units"]["count"].get("Citizen", 0) - resource_collectors - construction_workers

    def add_worker(self, building_type):
        # Must be one of the resource-producing buildings.
        if building_type not in ["Lumber Mill", "Mines", "Quarry", "Farm"]:
            return "not a valid building type"
        if self.player_stats["Buildings"]["levels"].get(building_type, 0) == 0:
            return "building not built"
        if self.number_of_available_workers() <= 0:
            return "no available workers"
        
        # Update in-memory stats.
        self.player_stats["Buildings"]["assigned_workers"][building_type] += 1
        
        # Also update the corresponding production_queue row.
        cur = self.db.cursor()
        cur.execute("""
            UPDATE production_queue
            SET number_of_workers = number_of_workers + 1
            WHERE player_id = ? AND production_type = 'resource' AND entity = ?
        """, (self.player_id, building_type))
        self.db.commit()
        return "Success"
    
    def remove_worker(self, building_type):
        # Must be one of the resource-producing buildings.
        if building_type not in ["Lumber Mill", "Mines", "Quarry", "Farm"]:
            return "not a valid building type"
        if self.player_stats["Buildings"]["assigned_workers"].get(building_type, 0) <= 0:
            return "no workers to remove"
        
        self.player_stats["Buildings"]["assigned_workers"][building_type] -= 1
        
        cur = self.db.cursor()
        # Update the worker count in the resource production record.
        cur.execute("""
            UPDATE production_queue
            SET number_of_workers = number_of_workers - 1
            WHERE player_id = ? AND production_type = 'resource' AND entity = ?
        """, (self.player_id, building_type))
        
        # For production types that are NOT research/construction, if the new number_of_workers is 0 then delete the row.
        cur.execute("""
            DELETE FROM production_queue
            WHERE player_id = ? 
              AND production_type NOT IN ('construction', 'unit_research') 
              AND entity = ?
              AND number_of_workers <= 0
        """, (self.player_id, building_type))
        self.db.commit()
        return "Success"

    def trade_possible(self, resources_cost):
        """
        Check if the player has enough resources for the trade cost.
        """
        for resource, amount in resources_cost.items():
            if self.player_stats["Resources"].get(resource, 0) < amount:
                return False
        return True

    def make_trade(self, resources_cost, resources_earned):
        """
        Directly perform a trade (e.g., with the merchant).
        Subtracts resources_cost (after checking if trade is possible and non‐negative)
        and adds resources_earned.
        """
        if not self.trade_possible(resources_cost):
            print("Not enough resources to make trade")
            return "not enough resources to make trade"
        
        # Ensure no negative values.
        for resource, value in resources_cost.items():
            if value < 0:
                msg = "resources_cost had a negative value: " + str(resources_cost)
                print(msg)
                return msg
        for resource, value in resources_earned.items():
            if value < 0:
                msg = "resources_earned had a negative value: " + str(resources_earned)
                print(msg)
                return msg

        # Deduct cost from player's resources.
        for resource, cost in resources_cost.items():
            self.player_stats["Resources"][resource] = self.player_stats["Resources"].get(resource, 0) - cost

        # Add earned resources.
        for resource, gain in resources_earned.items():
            self.player_stats["Resources"][resource] = self.player_stats["Resources"].get(resource, 0) + gain

        return "Success"

    def add_trade_offer(self, resources_cost, resources_earned):
        """
        Post a new trade offer and lock the cost resources.
        The offer is saved into the DB (as JSON text for the resource dictionaries).
        A player can only post as many offers as his Market level.
        """
        # Check that none of the values are negative.
        for resource, value in resources_cost.items():
            if value < 0:
                msg = "resources_cost had a negative value: " + str(resources_cost)
                print(msg)
                return msg
        for resource, value in resources_earned.items():
            if value < 0:
                msg = "resources_earned had a negative value: " + str(resources_earned)
                print(msg)
                return msg

        # Check if the player has built a Market.
        market_level = self.player_stats["Buildings"]["levels"].get("Market", 0)
        if market_level == 0:
            print("Market not built")
            return "Market not built"

        # Check if the player already has the maximum allowed offers for his Market level.
        cur = self.db.cursor()
        cur.execute("SELECT COUNT(*) as count FROM trade_offers WHERE player_id = ?", (self.player_id,))
        row = cur.fetchone()
        current_offers = row["count"] if row else 0
        if current_offers >= market_level:
            return "Max number of trades reached for Market level"

        # Check if the player has enough resources.
        if not self.check_if_player_has_enough_resources(resources_cost):
            msg = "player does not have enough resources: " + str(resources_cost)
            print(msg)
            return msg

        # Lock (subtract) the cost resources from the player.
        for resource, cost in resources_cost.items():
            self.player_stats["Resources"][resource] = self.player_stats["Resources"].get(resource, 0) - cost

        # Insert the new trade offer into the DB.
        cur.execute("""
            INSERT INTO trade_offers (player_id, resources_cost, resources_earned)
            VALUES (?, ?, ?)
        """, (self.player_id, json.dumps(resources_cost), json.dumps(resources_earned)))
        self.db.commit()

        return "Success"

    def remove_trade_offer(self, offer_id):
        """
        Cancel an existing trade offer (by its DB id) and refund the locked resources.
        This function checks that the offer belongs to the player.
        """
        cur = self.db.cursor()
        cur.execute("SELECT * FROM trade_offers WHERE id = ? AND player_id = ?", (offer_id, self.player_id))
        row = cur.fetchone()
        if not row:
            print("Trade offer not found")
            return "Trade not found"

        # Refund the locked cost resources back to the player.
        resources_cost = json.loads(row["resources_cost"])
        for resource, cost in resources_cost.items():
            self.player_stats["Resources"][resource] = self.player_stats["Resources"].get(resource, 0) + cost

        # Remove the trade offer from the DB.
        cur.execute("DELETE FROM trade_offers WHERE id = ? AND player_id = ?", (offer_id, self.player_id))
        self.db.commit()

        return "Success"

    def accept_offer(self, offer_id, other_player=None):
        """
        Accept a trade offer.
        If other_player is provided (i.e. someone is buying this offer) then check that the
        other player can pay the required resources (the offer’s trade price). In that case,
        subtract the price from the buyer and add the locked offer cost.
        Otherwise, if no other_player is provided, assume a self trade with the merchant –
        simply credit the earned resources to the offer maker.
        Finally, in all cases add the 'resources_earned' to the offer maker and delete the offer.
        """
        cur = self.db.cursor()
        cur.execute("SELECT * FROM trade_offers WHERE id = ?", (offer_id,))
        row = cur.fetchone()
        if not row:
            print("Trade offer not found")
            return "Trade offer not found"

        # If no other_player is specified, then the offer must belong to self.
        if other_player is None and row["player_id"] != self.player_id:
            return "Trade offer not owned by player"

        resources_cost = json.loads(row["resources_cost"])
        resources_earned = json.loads(row["resources_earned"])

        # If another player is accepting the offer, check and process his transaction.
        if other_player:
            if not other_player.trade_possible(resources_earned):
                print("not enough resources to make trade")
                return "not enough resources to make trade"
            # Grant the offer cost (i.e. what the offer maker is giving) to the accepting player,
            # and remove the cost of the trade (the price) from him.
            for resource, amount in resources_cost.items():
                other_player.player_stats["Resources"][resource] = other_player.player_stats["Resources"].get(resource, 0) + amount
            for resource, amount in resources_earned.items():
                other_player.player_stats["Resources"][resource] = other_player.player_stats["Resources"].get(resource, 0) - amount

        # In any case, credit the offer maker the resources he requested.
        # (Note: the offer maker had already locked away the cost when posting the offer.)
        for resource, amount in resources_earned.items():
            self.player_stats["Resources"][resource] = self.player_stats["Resources"].get(resource, 0) + amount

        # Remove the trade offer from the database.
        cur.execute("DELETE FROM trade_offers WHERE id = ?", (offer_id,))
        self.db.commit()

        return "Success"

class GameAPI:

    def __init__(self):
        self.init_db()

    def init_db(self):
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
                production_type TEXT,      -- 'contruction' or 'unit' or 'resource' or 'research'
                entity TEXT,               -- which building (e.g., 'Barracks') or unit (e.g., 'Barracks.Soldier' or 'Stables.Calvery') or resource (e.g., 'hay')
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

    def get_all_players(self):
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("SELECT player_id, name FROM players")
        rows = cur.fetchall()
        con.close()
        return rows

    def add_new_player(self, name, plain_password):
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

    def create_session(self, player_id, plain_password):

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

    def validate_session(self, player_id, session_auth):
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

    def update_unit_production(self, player_id, hours_passed, con):
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
        
        if groups == {}:
            return []
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

    def update_unit_research(self, player_id, hours_passed, con):
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

    def update_units(self, player_id, hours_passed, con):
        """
        Master update routine for units. This calls both the unit production and the 
        unit research update functions and returns a list of expected completion timestamps.
        These timestamps can then be used (for example) to inform when the next unit 
        or research upgrade will complete.
        """
        production_times = self.update_unit_production(player_id, hours_passed, con)
        research_times = self.update_unit_research(player_id, hours_passed, con)
        return production_times + research_times

    # ----------------------------------------------------------------
    def update_buildings(self, player_id, hours_passed, con):
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
            AND production_type = 'construction'
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
    def update_resources(self, player_id, hours_passed, con):
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
        bubm = game_config["game_speed_and_multiplier"]["building_upgrade_boost_multiplier"]
        uubm = game_config["game_speed_and_multiplier"]["unit_upgrade_boost_multiplier"]

        # Process building income/expenses.
        for b in player_buildings:
            b_type = b["building_type"]
            lvl = b["level"]
            if b_type in game_config["Buildings"]:
                hourly_cost = game_config["Buildings"][b_type]["hourly_cost"]
                for res, cost in hourly_cost.items():
                    delta = cost * hours_passed * gs * bs * church_multiplier * bubm ** (lvl - 1)
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
                    delta = cost * count * hours_passed * gs * us * church_multiplier * uubm ** (lvl - 1)
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

            rate = workers * hours_passed * gs * rs * church_multiplier * bubm ** (bld_level - 1)
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
            pass#cur.execute("UPDATE resources SET {} = {} + ? WHERE player_id = ?".format(res, res), (delta, player_id))

        return []

    def update_quests(self, player_id, con):
        """
        Checks each quest configuration. In our quest config each quest contains:
            • func: a condition expressed (for example) as "Resources['diamond'] >= 5".
            • reward: a string with one or more entries like "Resources.money = 1000" separated by '&'.
        If the quest (which is not already completed) evaluates to True, the reward is applied and
        the quest is marked complete (both in self.player_stats["Quests"] and—if desired—in the DB).
        """
        # Build an evaluation environment with keys for Resources, Units, and Buildings.
        # Note: We use the dictionaries from the player_stats.
        env = {
            "Resources": self.player_stats["Resources"],
            # For units, we assume that it is the count that matters (for quest conditions)
            "Units": self.player_stats["Units"]["count"],
            "Buildings": self.player_stats["Buildings"]["levels"],
        }
        
        completed_quests = []
        for quest in game_config["Quests"]:
            qid = quest["id"]
            # Check if the quest is already marked complete in player_stats.
            if self.player_stats["Quests"].get(qid, False):
                continue  # already completed
            # Evaluate the quest condition.
            try:
                # The func string should be written so that, for example, Resources['diamond'] >= 5.
                if eval(quest["func"], {}, env):
                    # Quest is complete. Mark as complete.
                    self.player_stats["Quests"][qid] = True
                    completed_quests.append(qid)
                    
                    # Now parse and apply the reward.
                    # The reward string uses ampersand (&) to separate multiple rewards.
                    reward_entries = quest["reward"].split("&")
                    for entry in reward_entries:
                        entry = entry.strip()  # e.g. "Resources.money = 1000"
                        if "=" not in entry:
                            continue
                        left, right = entry.split("=", 1)
                        left = left.strip()
                        right = right.strip()
                        # In our config rewards we expect the left side to be of the form "Resources.<resource_name>"
                        if left.startswith("Resources."):
                            resource_name = left[len("Resources."):]
                            try:
                                amount = float(right)
                            except ValueError:
                                amount = 0
                            self.player_stats["Resources"][resource_name] = \
                                self.player_stats["Resources"].get(resource_name, 0) + amount
                            print("Quest", qid, "completed: Awarded", amount, resource_name)
                        else:
                            print("Reward parse warning: unknown key in:", left)
            except Exception as e:
                print("Error evaluating quest", qid, "condition:", e)
        return completed_quests

    def update_progress(self, player_id):
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
        
        # ... you could call update_buildings(player_id, hours_passed, con) and update_resources(player_id, hours_passed, con) here
        resources_ts = self.update_resources(player_id, hours_passed, con)
        units_ts = self.update_units(player_id, hours_passed, con)
        building_ts = self.update_buildings(player_id, hours_passed, con)
        quests_ts = self.update_quests(player_id, con)

        # Update the player's last_update time.
        cur.execute("UPDATE players SET last_update = ? WHERE player_id = ?", (now.strftime("%Y-%m-%d %H:%M:%S"), player_id))
        
        con.commit()
        con.close()
        
        return resources_ts + units_ts + building_ts + quests_ts


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
            if game_config["Buildings"][building]["hourly_cost"][potential_bad_resrouce] > 0:
                print(f"WARNING: {building} has a postive hourly cost for {potential_bad_resrouce}. Players will loose money hourly after building this (typically building produce money). Make sure this is intended")


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
            if "Buildings" in potential_bad_item:
                potential_bad_item = potential_bad_item.split(".")[1]
                assert potential_bad_item in all_buildings, f"Incorrect building {potential_bad_item} in {quest} requirements"
            elif "Resources" in potential_bad_item:
                potential_bad_item = potential_bad_item.split(".")[1]
                assert potential_bad_item in all_resources, f"Incorrect resource {potential_bad_item} in {quest} requirements"
            elif "Units" in potential_bad_item:
                potential_bad_item = potential_bad_item.split(".",1)[1]
                assert potential_bad_item in all_units, f"Incorrect unit {potential_bad_item} in {quest} requirements"

            #elfit it must only contain digits and >=< signs
            else:
                for char in potential_bad_item:
                   assert char in "1234567890<=>&", f"Incorrect resource {potential_bad_item} in {quest} requirements"

        for potential_bad_item in quest["reward"].split(" "):
            if "Resource" in potential_bad_item:
                potential_bad_item = potential_bad_item.split(".")[1]
                assert potential_bad_item in all_resources, f"Incorrect resource {potential_bad_item} in {quest} rewards"
            else:
                for char in potential_bad_item:
                   assert char in "1234567890=&", f"Incorrect resource {potential_bad_item} in {quest} rewards"

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


# If run as a script, initialize the DB.
if __name__ == '__main__':
    game_api = GameAPI()
    # To test adding a new player:
    new_player_id = game_api.add_new_player("Player 1","password")
    session_id = game_api.create_session(new_player_id, "password")
    
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

