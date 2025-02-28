import random
import datetime
upgrade_multiplier = 2.2
production_multiplier = 1.25

global_trades = [
    {"resources_cost": {"money": 1000}, "resources_earned": {"diamond": 1}},
    {"resources_cost": {"money": 200}, "resources_earned": {"gold": 1}},
    {"resources_cost": {"money": 50}, "resources_earned": {"iron": 1}}
]

quests = [
    {"text": "Collect 5 diamonds", "reward": 500, "func": lambda player: player.player_stats['Resources']['diamond'] >= 5},
    {"text": "Gather 50 hay", "reward": 250, "func": lambda player: player.player_stats['Resources']['hay'] >= 50},
    {"text": "Amass 100 iron", "reward": 500, "func": lambda player: player.player_stats['Resources']['iron'] >= 100},
    {"text": "Accumulate 25 gold", "reward": 500, "func": lambda player: player.player_stats['Resources']['gold'] >= 25},
    {"text": "Stockpile 100 stone", "reward": 250, "func": lambda player: player.player_stats['Resources']['stone'] >= 100},
    {"text": "Train 10 soldiers", "reward": 300, "func": lambda player: player.player_stats['Units']['count']['Soldier'] >= 10},
    {"text": "Have 8 buildings", "reward": 400, "func": lambda player: sum(player.player_stats['Buildings']['levels'].values()) >= 8},
    {"text": "Have 15 buildings", "reward": 800, "func": lambda player: sum(player.player_stats['Buildings']['levels'].values()) >= 15},
    {"text": "Harvest 100 wood", "reward": 200, "func": lambda player: player.player_stats['Resources']['wood'] >= 100},
    {"text": "Forge 2 boats", "reward": 600, "func": lambda player: player.player_stats['Units']['count']['Boat'] >= 2},
    {"text": "Conscript 5 cavalry", "reward": 350, "func": lambda player: player.player_stats['Units']['count']['Calvary'] >= 5},
    {"text": "Construct a grand church", "reward": 800, "func": lambda player: player.player_stats['Buildings']['levels']['Church'] >= 1},
]

game_config = {
    "Buildings": {
        "Castle": {
            "description": "A place to incrase your number of buildings by 5",
            "cost": {
                "money": 1000,
                "hay": 10,
                "wood": 10,
            },
            "hourly_cost": {
                "money": -50,
            },
            "max": 6,
            "hours_to_build": 4,
        },


        "Village House": {
            "description": "A house for 5 villagers to live in.",
            "cost": {
                "money": 1000,
                "stone": 5,
            },
            "hourly_cost": {
                "money": -20,
            },
            "max": 10,
            "hours_to_build": 3,
        },
        "Market": {
            "description": "A market to trade resources. Upgrading provides better and more trades per day",
            "cost": {
                "money": 2000,
                "stone": 5,
                "wood": 30,
            },
            "hourly_cost": {
                "money": -20,
            },
            "max": 3,
            "hours_to_build": 6,
        },
        
        "Smithy": {
            "description": "Boosts all training by 1.2x and upgrade units",
            "cost": {
                "money": 10000,
                "diamond": 2,
                "iron": 20,
                "stone": 50,
            },
            "hourly_cost": {
                "money": -50,
            },
            "max": 1,
            "hours_to_build": 24,
        },
        "Church": {
            "description": "Boosts all resource resource production by 1.25x",
            "cost": {
                "money": 10000,
                "diamond": 2,
                "gold": 6,
                "stone": 50,
            },
            "hourly_cost": {
                "money": -50,
            },
            "max": 1,
            "hours_to_build": 24,
        },
        "Colosseum": {
            "description": "Boosts all attack by 1.2x",
            "cost": {
                "money": 10000,
                "diamond": 2,
                "iron": 20,
                "stone": 50,
            },
            "hourly_cost": {
                "money": -50,
            },
            "max": 1,
            "hours_to_build": 24,
        },

        "Farm": {
            "description": "Produces hay. Upgrading boosts product by " + str(upgrade_multiplier) + "x",
            "cost": {
                "money": 1000,
                "wood": 20,
            },
            "hourly_cost": {
                "money": -20,
            },
            "max": 3,
            "hours_to_build": 6,
        },
        
        "Lumber Mill": {
            "description": "Produces wood. Upgrading boosts product by " + str(upgrade_multiplier) + "x",
            "cost": {
                "money": 1000,
                "stone": 15,
                "hay": 20,
            },
            "hourly_cost": {
                "money": -20,
            },  
            "max": 3,
            "hours_to_build": 6,
        },
        
        "Quarry": {
            "description": "Produces stone. Upgrading boosts product by " + str(upgrade_multiplier) + "x",
            "cost": {
                "money": 1000,
                "wood": 20,
                "hay": 20,
            },
            "hourly_cost": {
                "money": -20,
            },
            "max": 3,
            "hours_to_build": 6,
        },
        
        "Mines": {
            "description": "Produces iron. Upgrading boosts product by " + str(upgrade_multiplier) + "x",
            "cost": {
                "money": 1000,
                "stone": 20,
                "wood": 25,
            },
            "hourly_cost": {
                "money": -20,
            },
            "max": 3,
            "hours_to_build": 6,
        },
        "Barracks": {
            "description": "Trains soldiers. Upgrading boosts training speed by " + str(upgrade_multiplier) + "x",
            "cost": {
                "money": 2000,
                "hay": 20,
                "wood": 25,
                "iron": 10,
            },
            "hourly_cost": {
                "money": -20,
            },
            "max": 3,
            "hours_to_build": 6,
        },
        "Stables": {
            "description": "Trains calvary. Upgrading boosts training speed by " + str(upgrade_multiplier) + "x",
            "cost": {
                "money": 2000,
                "hay": 20,
                "iron": 100,
            },
            "hourly_cost": {
                "money": -20,
            },
            "max": 3,
            "hours_to_build": 12,
        },
        
        "Dock": {
            "description": "A dock to construct boats. Upgrading imporves boat construction speed by " + str(upgrade_multiplier) + "x",
            "cost": {
                "money": 2500,
                "stone": 5,
                "wood": 30,
            },
            "hourly_cost": {
                "money": -20,
            },
            "max": 3,
            "hours_to_build": 6,
        },
        "Keep": {
            "description": "Produces Dukes. Used for conquering other villages.",
            "cost": {
                "money": 30000,
                "diamond": 2,
                "gold": 20,
                "stone": 50,
            },
            "hourly_cost": {
                "money": -200,
            },
            "max": 1,
            "hours_to_build": 48,
        },
        
        "Walls": {
            "description": "Protects your village from enemies by 5% per level",
            "cost": {
                "money": 500,
                "stone": 10,
            },
            "hourly_cost": {
                "money": -20,
            },
            "max": 10,
            "hours_to_build": 1,
        },

    },
    "Units": {
        "Citizen": {
            "description": "A citizen to work in your village or turn into a soldier",
            "cost": {
                "money": 100,
                "hay": 4,
            },
            "hourly_cost": {
                "money": 10,
            },
            "max": 1,
            "hours_to_build": .5,
            "attack": 5,
            "defense": 8,
            "archer_defense": 8,
            "calvary_defense": 5,
            "building_source": "Castle",
            "upgrade_cost": {}
        },
        "Soldier": {
            "description": "A soldier to defend your village",
            "cost": {
                "money": 200,
                "hay": 20,
            },
            "hourly_cost": {
                "money": 30,
            },
            "max": 3,
            "hours_to_build": 1,
            "attack": 10,
            "defense": 10,
            "archer_defense": 10,
            "calvary_defense": 10,
            "building_source": "Barracks",
            "upgrade_cost": {
                "money": 1000,
                "hay": 50,
                "iron": 100,
                "gold": 5,
            }
        },
        "Calvary": {
            "description": "A calvary to defend your village",
            "cost": {
                "money": 300,
                "hay": 10,
                "iron": 50,
            },
            "hourly_cost": {
                "money": 50,
            },
            "max": 3,
            "hours_to_build": 1.5,
            "attack": 15,
            "defense": 10,
            "archer_defense": 10,
            "calvary_defense": 10,
            "building_source": "Stables",  
            "upgrade_cost": {
                "money": 1500,
                "hay": 25,
                "iron": 200,
                "gold": 8,
            } 
        },
        "Archer": {
            "description": "An archer to defend your village",
            "cost": {
                "money": 250,
                "hay": 4,
                "wood": 50,
            },
            "hourly_cost": {
                "money": 50,
            },
            "max": 3,
            "hours_to_build": 2,
            "attack": 10,
            "defense": 15,
            "archer_defense": 10,
            "calvary_defense": 10,
            "building_source": "Barracks",
            "upgrade_cost": {
                "money": 1000,
                "hay": 25,
                "wood": 100,
                "gold": 5,
            }
        },
        "Duke": {
            "description": "A duke to conquer other villages.",
            "cost": {
                "money": 10000,
                "hay": 20,
                "iron": 20,
                "gold": 20,
                "diamond": 2,
            },
            "hourly_cost": {
                "money": 200,
            },
            "max": 1,
            "hours_to_build": 24,
            "attack": 30,
            "defense": 30,
            "archer_defense": 30,
            "calvary_defense": 30,
            "building_source": "Keep",
            "upgrade_cost": {}
        },
        "Boat": {
            "description": "A boat used to cary resources and soldiers to other lands.",
            "cost": {
                "money": 1000,
                "wood": 100,
            },
            "hourly_cost": {
                "money": 100,
            },
            "max": 3,
            "hours_to_build": 6,
            "attack": 0,
            "defense": 0,
            "archer_defense": 0,
            "calvary_defense": 0,
            "building_source": "Dock",
            "upgrade_cost": {
                "money": 1000,
                "wood": 100,
            }
        },
    }
}

PlayerStats = {
    "Name": "Player 1",
    "Buildings": {
        "levels":  {    
            "Castle": 1,
            "Village House": 1,
            "Dock": 0,
            "Market": 0,
            "Walls": 0,
            "Church": 0,
            "Colosseum": 0,
            "Smithy": 0,
            "Farm": 1,
            "Quarry": 0,
            "Keep": 0,
            "Lumber Mill": 1,
            "Mines": 0,
            "Barracks": 0,
            "Stables": 0,
        },
        #None if not building, otherwise float between 0 and 1 on progress
        "ongoing_builds": {
            "Castle": None,
            "Village House": None,
            "Dock": None,
            "Market": None,
            "Walls": None,
            "Church": None,
            "Colosseum": None,
            "Smithy": None,
            "Farm": None,
            "Quarry": None,
            "Keep": None,
            "Lumber Mill": None,
            "Mines": None,
            "Barracks": None,
            "Stables": None,
        },
        #a float between 0 and 1 on progress
        "production": {
            "Castle": 0.0,
            "Village House": 0.0,
            "Dock": 0.0,
            "Market": 0.0,
            "Walls": 0.0,
            "Church": 0.0,
            "Colosseum": 0.0,
            "Smithy": 0.0,
            "Farm": 0.0,
            "Quarry": 0.0,
            "Keep": 0.0,
            "Lumber Mill": 0.0,
            "Mines": 0.0,
            "Barracks": 0.0,
            "Stables": 0.0,
        },
        "assigned_workers": {
            "Castle": 0,
            "Village House": 0,
            "Dock": 0,
            "Market": 0,
            "Walls": 0,
            "Church": 0,
            "Colosseum": 0,
            "Smithy": 0,
            "Farm": 0,
            "Quarry": 0,
            "Keep": 0,
            "Lumber Mill": 0,
            "Mines": 0,
            "Barracks": 0,
            "Stables": 0,
        },
    },
    "Units": {
        "count": {
            "Citizen": 3,
            "Soldier": 0,
            "Calvary": 0,
            "Archer": 0,
            "Duke": 0,
            "Boat": 0,
        },
        "levels": {
            "Citizen": 1,
            "Soldier": 0,
            "Calvary": 0,
            "Archer": 0,
            "Duke": 1,
            "Boat": 1,
        },
        "ongoing_builds": {
            "Citizen": None,
            "Soldier": None,
            "Calvary": None,
            "Archer": None,
            "Duke": None,
            "Boat": None,
        },
        "ongoing_upgrades": {
            "Citizen": None,
            "Soldier": None,
            "Calvary": None,
            "Archer": None,
            "Duke": None,
            "Boat": None,
        },
        "queued_builds": {
            "Citizen": 0,
            "Soldier": 0,
            "Calvary": 0,
            "Archer": 0,
            "Duke": 0,
            "Boat": 0,
        },
    },
    "Resources": {
        "money": 500,
        "stone": 0,
        "iron": 0,
        "gold": 0,
        "diamond": 0,
        "wood": 5,
        "hay": 5,
    },
    "Quests": [False] *50,
    "Market": {
        "listings":     #list of dicts
            []
            # {"resources_cost": {
            #     "money": 0,
            #     "stone": 0,
            #     "iron": 0,
            #     "gold": 0,
            #     "diamond": 0,
            #     "wood": 0,
            # },
            # "resources_earned": {
            #     "money": 0,
            #     "stone": 0,
            #     "iron": 0,
            #     "gold": 0,
            #     "diamond": 0,
            #     "wood": 0,
            # }},
        
    }
}

class Player:
    def __init__(self, name="player", load_config = None):
        if not load_config:
            self.player_stats = PlayerStats.copy()
            self.player_stats["Name"] = name
        else:
            self.player_stats = load_config

        self.last_update = datetime.datetime.now()

          
    def export_player_values(self):
        return self.player_stats

    def update(self, speed = 3.0):
        """ Update resources based on the time elapsed. """
        now = datetime.datetime.now()
        hours_passed = (now - self.last_update).total_seconds() / 3600
        hours_passed = hours_passed * speed

        self.update_resources(hours_passed)
        self.update_buildings(hours_passed)
        self.update_unit_upgrades(hours_passed)
        self.update_units(hours_passed)
        self.update_quests()
        # Update money

        self.last_update = now

    def update_resources(self, hours_passed):
        """ Update resources based on the time elapsed. """
        church_boost = (1.2 ** self.player_stats["Buildings"]["levels"]["Church"])

        # Update money
        income = 0


        for building in self.player_stats["Buildings"]["levels"]:
            building_level = self.player_stats["Buildings"]["levels"][building]
            hourly_cost = game_config["Buildings"][building]["hourly_cost"]
            income += building_level * - hourly_cost["money"]
        
        for unit in self.player_stats["Units"]["levels"]:
            unit_count = self.player_stats["Units"]["count"][unit]
            hourly_cost = game_config["Units"][unit]["hourly_cost"]
            income += unit_count * - hourly_cost["money"]
        
        self.player_stats["Resources"]["money"] += income * hours_passed * church_boost


        # update hay progress given how much works are assigned
        farm_level = self.player_stats["Buildings"]["levels"]["Farm"]
        num_workers = self.player_stats["Buildings"]["assigned_workers"]["Farm"]
        self.player_stats["Buildings"]["production"]["Farm"] += (production_multiplier ** (farm_level -1 )) * num_workers * hours_passed * church_boost
        if self.player_stats["Buildings"]["production"]["Farm"] >= 1:
            self.player_stats["Resources"]["hay"] += int(self.player_stats["Buildings"]["production"]["Farm"])
            self.player_stats["Buildings"]["production"]["Farm"] = self.player_stats["Buildings"]["production"]["Farm"] - int(self.player_stats["Buildings"]["production"]["Farm"])

        # update lumber progress given how much works are assigned
        lumber_mill_level = self.player_stats["Buildings"]["levels"]["Lumber Mill"]
        num_workers = self.player_stats["Buildings"]["assigned_workers"]["Lumber Mill"]
        self.player_stats["Buildings"]["production"]["Lumber Mill"] += (production_multiplier ** (lumber_mill_level -1)) * num_workers * hours_passed * church_boost
        if self.player_stats["Buildings"]["production"]["Lumber Mill"] >= 1:
            self.player_stats["Resources"]["wood"] += int(self.player_stats["Buildings"]["production"]["Lumber Mill"])
            self.player_stats["Buildings"]["production"]["Lumber Mill"] = self.player_stats["Buildings"]["production"]["Lumber Mill"] - int(self.player_stats["Buildings"]["production"]["Lumber Mill"])


        # update stone progress given how much works are assigned
        quarry_level = self.player_stats["Buildings"]["levels"]["Quarry"]
        num_workers = self.player_stats["Buildings"]["assigned_workers"]["Quarry"]
        self.player_stats["Buildings"]["production"]["Quarry"] += (production_multiplier ** (quarry_level -1)) * num_workers * hours_passed * church_boost
        if self.player_stats["Buildings"]["production"]["Quarry"] >= 1:
            self.player_stats["Resources"]["stone"] += int(self.player_stats["Buildings"]["production"]["Quarry"])
            self.player_stats["Buildings"]["production"]["Quarry"] = self.player_stats["Buildings"]["production"]["Quarry"] - int(self.player_stats["Buildings"]["production"]["Quarry"])

        # update iron progress given how much works are assigned
        iron_mine_level = self.player_stats["Buildings"]["levels"]["Mines"]
        num_workers = self.player_stats["Buildings"]["assigned_workers"]["Mines"]
        self.player_stats["Buildings"]["production"]["Mines"] += (production_multiplier ** (iron_mine_level -1)) * num_workers * hours_passed * church_boost
        if self.player_stats["Buildings"]["production"]["Mines"] >= 1:
            #has a chance to produce diamon and gold as well
            for _ in range(int(self.player_stats["Buildings"]["production"]["Mines"])):

                roll = random.randint(1, 100)
                if roll <= 5:
                    self.player_stats["Resources"]["diamond"] += 1
                elif roll <= 20:
                    self.player_stats["Resources"]["gold"] += 1
                else:
                    self.player_stats["Resources"]["iron"] += 1

            self.player_stats["Buildings"]["production"]["Mines"] = self.player_stats["Buildings"]["production"]["Mines"] - int(self.player_stats["Buildings"]["production"]["Mines"])

    def update_buildings(self, hours_passed):
        """ Update building progress. """
        for building in self.player_stats["Buildings"]["ongoing_builds"]:
            if self.player_stats["Buildings"]["ongoing_builds"][building] != None:
                #add building time for every building level
                building_level = self.player_stats["Buildings"]["levels"][building]
                self.player_stats["Buildings"]["ongoing_builds"][building] += hours_passed / (game_config["Buildings"][building]["hours_to_build"] * (upgrade_multiplier ** (building_level-1)))
                if self.player_stats["Buildings"]["ongoing_builds"][building] >= 1:
                    self.player_stats["Buildings"]["levels"][building] += 1
                    self.player_stats["Buildings"]["ongoing_builds"][building] = None

    def update_units(self, hours_passed):
        """ Update unit progress. """
        #boost from smithy
        smithy_boost = (1.2 ** self.player_stats["Buildings"]["levels"]["Smithy"])

        for unit in self.player_stats["Units"]["ongoing_builds"]:

            #if queue is not empty but ongoing_builds is None let it start building
            if self.player_stats["Units"]["queued_builds"][unit] > 0 and self.player_stats["Units"]["ongoing_builds"][unit] == None:
                self.player_stats["Units"]["ongoing_builds"][unit] = 0.0
                self.player_stats["Units"]["queued_builds"][unit] -= 1

            if self.player_stats["Units"]["ongoing_builds"][unit] != None:

                #use building_source to get building level and multiply by upgrade_multiplier
                building_source = game_config["Units"][unit]["building_source"]
                building_level = self.player_stats["Buildings"]["levels"][building_source]

                self.player_stats["Units"]["ongoing_builds"][unit] += (hours_passed / game_config["Units"][unit]["hours_to_build"]) * smithy_boost * (upgrade_multiplier ** (building_level - 1))
                if self.player_stats["Units"]["ongoing_builds"][unit] >= 1:
                    self.player_stats["Units"]["count"][unit] += 1

                    #if queue is not empty
                    if self.player_stats["Units"]["queued_builds"][unit] > 0:
                        self.player_stats["Units"]["queued_builds"][unit] -= 1
                        self.player_stats["Units"]["ongoing_builds"][unit] = 0.0

                    else:  
                        self.player_stats["Units"]["ongoing_builds"][unit] = None
    
    def update_unit_upgrades(self, hours_passed):
        """ Update unit upgrade progress. """
        #boost from smithy
        for unit in self.player_stats["Units"]["ongoing_upgrades"]:
            if self.player_stats["Units"]["ongoing_upgrades"][unit] != None:

                #use building_source to get building level and multiply by upgrade_multiplier to speed up upgrade
                building_source = game_config["Units"][unit]["building_source"]
                building_level = self.player_stats["Buildings"]["levels"][building_source]

                #use unit current level to get upgrade cost and multiply by upgrade_multiplier to reduce speed to upgrade
                unit_level = self.player_stats["Units"]["levels"][unit]

                self.player_stats["Units"]["ongoing_upgrades"][unit] += (hours_passed / (game_config["Units"][unit]["hours_to_build"] * (upgrade_multiplier ** (unit_level - 1))))
                if self.player_stats["Units"]["ongoing_upgrades"][unit] >= 1:
                    self.player_stats["Units"]["levels"][unit] += 1
                    self.player_stats["Units"]["ongoing_upgrades"][unit] = None

    def update_quests(self):
        """ Check if quests are completed. """
        for i in range(len(quests)):
            if not self.player_stats["Quests"][i]:
                #if quest is already completed skip
                if self.player_stats["Quests"][i]:
                    continue

                if quests[i]["func"](self):
                    self.player_stats["Resources"]["money"] += quests[i]["reward"]
                    self.player_stats["Quests"][i] = True

    def purchase_unit(self, unit_type):
        #TODO add one build at a time
        if unit_type not in game_config["Units"]:
            return "Not a valid unit type"
        
        #check if building requiriment is met
        building_source = game_config["Units"][unit_type]["building_source"]
        building_level = self.player_stats["Buildings"]["levels"][building_source]
        if building_level == 0:
            return  building_source + " must be built first"
        
        #find level of unit
        unit_level = self.player_stats["Units"]["levels"][unit_type]
        
        if unit_level == 0:
            return "Unit level is 0, please unlock by upgrading in Smithy"
        
        #if unit is a Citizen make sure queue + ongoing_builds + citizens is less then village house level *5
        if unit_type == "Citizen":
            #1 if not none else 0
            current_produceing = 1 if self.player_stats["Units"]["ongoing_builds"][unit_type] != None else 0
            in_queue = self.player_stats["Units"]["queued_builds"][unit_type]
            current_count = self.player_stats["Units"]["count"][unit_type]
            if current_produceing + in_queue + current_count >= self.player_stats["Buildings"]["levels"]["Village House"] * 5:
                return "Please Upgrade Village House"
        
        #check if enough resources
        unit_cost = game_config["Units"][unit_type]["cost"].copy()
        #multiply all costs by cost multiplier)
        for resource in unit_cost:
            unit_cost[resource] = unit_cost[resource] * (upgrade_multiplier **(unit_level - 1))
        
        if not self.check_if_player_has_enough_resources(unit_cost):
            return "Not Enough Resources"
        
        #add to queue
        self.player_stats["Units"]["queued_builds"][unit_type] += 1

        
        #subtract resources
        for resource in unit_cost:
            self.player_stats["Resources"][resource] -= unit_cost[resource] 

        return "Success"
    
    def remove_unit_from_queue(self, unit_type):
        #refund all unit costs and remove from queue or set ongoing_builds to 0.0

        #check if unit_type is in game_config
        if unit_type not in game_config["Units"]:
            return "Not a valid unit type"

        if self.player_stats["Units"]["queued_builds"][unit_type] == 0 and self.player_stats["Units"]["ongoing_builds"][unit_type] == None:
            return "No units in queue"
        
        #check queue
        if self.player_stats["Units"]["queued_builds"][unit_type] > 0:
            self.player_stats["Units"]["queued_builds"][unit_type] -= 1

        elif self.player_stats["Units"]["ongoing_builds"][unit_type] != None:
            self.player_stats["Units"]["ongoing_builds"][unit_type] = None

    


        #refund
        unit_level = self.player_stats["Units"]["levels"][unit_type]
        unit_cost = game_config["Units"][unit_type]["cost"]
        #multiply all costs by cost multiplier)
        for resource in unit_cost:
            unit_cost[resource] = unit_cost[resource] * (upgrade_multiplier **(unit_level-1))
        
        for resource in unit_cost:
            self.player_stats["Resources"][resource] += unit_cost[resource] 

        return "Success"

        
    def purchase_building(self, building_type):
        #first check if there is an avalible worker for him to become a builder
        if self.number_of_available_workers() > 0:
            #check if building_type is in game_config
            if building_type not in game_config["Buildings"]:
                return "Not a valid building type"
            
            #check if building_type is max level
            if self.player_stats["Buildings"]["levels"][building_type] == game_config["Buildings"][building_type]["max"]:
                return "Max Level Reached"
            
            #check if ongoing upgrade for that building
            if self.player_stats["Buildings"]["ongoing_builds"][building_type] != None:
                return "Already Upgrading"
            
            #check if castle level allows for more builds
            ongoing_building_upgrades = len([building for building in self.player_stats["Buildings"]["ongoing_builds"] if self.player_stats["Buildings"]["ongoing_builds"][building] != None])
            number_of_buildings = sum(self.player_stats["Buildings"]["levels"].values())
            if building_type != "Castle" and number_of_buildings + ongoing_building_upgrades >= self.player_stats["Buildings"]["levels"]["Castle"] * 5:
                return "Not Enough Castle Level"

            
            #find cost of building
            building_cost = game_config["Buildings"][building_type]["cost"].copy()
            #multiply all costs by cost multiplier)
            building_level = self.player_stats["Buildings"]["levels"][building_type]
            for resource in building_cost:
                building_cost[resource] = building_cost[resource] * (upgrade_multiplier **(building_level))
            
            #check if player has enough resources
            if not self.check_if_player_has_enough_resources(building_cost):
                return "Not Enough Resources"
            
            #subtract resources
            for resource in building_cost:
                self.player_stats["Resources"][resource] -= building_cost[resource]
            
            #start building unit
            self.player_stats["Buildings"]["ongoing_builds"][building_type] = 0.0
            return "Success"
        else:
            return "Not Enough Workers avalible"
                  
    def upgrade_unit(self, unit_type):

        #check if smithy is built
        if self.player_stats["Buildings"]["levels"]["Smithy"] == 0:
            return "Smithy must be built first"
        
        #check if not already upgrading anything
        for unit in self.player_stats["Units"]["ongoing_upgrades"]:
            if self.player_stats["Units"]["ongoing_upgrades"][unit] != None:
                return "Already Upgrading"

        #check if unit_type is in game_config
        if unit_type not in game_config["Units"]:
            return "Not a valid unit type"
        
        #check if unit_type is max level
        if self.player_stats["Units"]["levels"][unit_type] == game_config["Units"][unit_type]["max"]:
            return "Max Level Reached"
        
        #find cost of unit upgrade

        unit_cost = game_config["Units"][unit_type]["upgrade_cost"]
        #multiply all costs by cost multiplier)
        unit_level = self.player_stats["Units"]["levels"][unit_type]
        for resource in unit_cost:
            unit_cost[resource] = unit_cost[resource] * (upgrade_multiplier **(unit_level))
        
        #check if player has enough resources
        if not self.check_if_player_has_enough_resources(unit_cost):
            return "Not Enough Resources"
        
        #subtract resources
        for resource in unit_cost:
             self.player_stats["Resources"][resource] -= unit_cost[resource]
        
        #start building unit
        self.player_stats["Units"]["ongoing_upgrades"][unit_type] = 0.0
        return "Success"

    def check_if_player_has_enough_resources(self, resources_dict):
        #example resources_dict = {"money": 100, "stone": 10, "iron": 5}
        for resource in resources_dict:
            if self.player_stats["Resources"][resource] < resources_dict[resource]:
                return False

        return True

    def number_of_available_workers(self):
        #find number of builders + training_queie + training + farmers + miners + lumberjacks + Minesrs

        resource_collectors = self.player_stats["Buildings"]["assigned_workers"]["Farm"] + self.player_stats["Buildings"]["assigned_workers"]["Quarry"] + self.player_stats["Buildings"]["assigned_workers"]["Lumber Mill"] + self.player_stats["Buildings"]["assigned_workers"]["Mines"]
        #training = self.player_stats["Units"]["queued_builds"]["Soldier"] + self.player_stats["Units"]["queued_builds"]["Calvary"] + self.player_stats["Units"]["queued_builds"]["Archer"] + self.player_stats["Units"]["queued_builds"]["Duke"] 
        #num of on_going builds that is not equal to None
        construction_workers = len([building for building in self.player_stats["Buildings"]["ongoing_builds"] if self.player_stats["Buildings"]["ongoing_builds"][building] != None])
        #training += self.player_stats["Units"]["queued_builds"]["Boat"] #TODO decide if boat should be included
        return self.player_stats["Units"]["count"]["Citizen"] - resource_collectors - construction_workers
  
    def add_worker(self, building_type):
        #must be Lumber Mill, Mines, Quarry, or Farm
        if building_type is not None and building_type not in ["Lumber Mill", "Mines", "Quarry", "Farm"]:
            print("not a valid building type: " + building_type)
            return "not a valid building type"
        #check if building is built
        if self.player_stats["Buildings"]["levels"][building_type] == 0:
            print("building not built: " + building_type)
            return "building not built"
        #check if there is an available worker
        if self.number_of_available_workers() <= 0:
            return "no available workers"
        #add worker
        self.player_stats["Buildings"]["assigned_workers"][building_type] += 1
        return "Success"
    
    def remove_worker(self, building_type):
        #must be Lumber Mill, Mines, Quarry, or Farm
        if building_type not in ["Lumber Mill", "Mines", "Quarry", "Farm"]:
            print("not a valid building type")
            return "not a valid building type"
        #check if there is an available worker
        if self.player_stats["Buildings"]["assigned_workers"][building_type] <= 0:
            return "no workers to remove"
        #remove worker
        self.player_stats["Buildings"]["assigned_workers"][building_type] -= 1
        return "Success"

    def make_trade(self, resources_cost, resources_earned,):
        """ Make a trade with the merchant. """

        if not self.trade_possible(resources_cost):
            print("not enough resources to make trade")
            return "not enough resources to make trade"
        
        #check if resources_earned and resources_cost are above 0
        for resource in resources_cost:
            if resources_cost[resource] < 0:
                print("resources_cost had a negative value: " +  str(resources_cost))
                return "resources_cost had a negative value" +  str(resources_cost)
        for resource in resources_earned:
            if resources_earned[resource] < 0:
                print("resources_cost had a negative value: " + str(resources_earned))
                return "resources_cost had a negative value" + str(resources_earned)
            

        if 'money' in resources_cost:
            self.player_stats["Resources"]["money"] -= resources_cost["money"]
        if "stone" in resources_cost:
            self.player_stats["Resources"]["stone"] -= resources_cost["stone"]
        if "iron" in resources_cost:
            self.player_stats["Resources"]["iron"] -= resources_cost["iron"]
        if "gold" in resources_cost:
            self.player_stats["Resources"]["gold"] -= resources_cost["gold"]
        if "diamond" in resources_cost:
            self.player_stats["Resources"]["diamond"] -= resources_cost["diamond"]
        if "wood" in resources_cost:
            self.player_stats["Resources"]["wood"] -= resources_cost["wood"]

        if 'money' in resources_earned:
            self.player_stats["Resources"]["money"] += resources_earned["money"]
        if "stone" in resources_earned:
            self.player_stats["Resources"]["stone"] += resources_earned["stone"]
        if "iron" in resources_earned:
            self.player_stats["Resources"]["iron"] += resources_earned["iron"]
        if "gold" in resources_earned:
            self.player_stats["Resources"]["gold"] += resources_earned["gold"]
        if "diamond" in resources_earned:
            self.player_stats["Resources"]["diamond"] += resources_earned["diamond"]
        if "wood" in resources_earned:
            self.player_stats["Resources"]["wood"] += resources_earned["wood"]

        return "Success"
                
    def trade_possible(self, resources_cost):
        """ Check if a trade is possible. """
        #check for negative values to
        if 'money' in resources_cost:
            if self.player_stats["Resources"]["money"] < resources_cost["money"]:
                return False
        if "stone" in resources_cost:
            if self.player_stats["Resources"]["stone"] < resources_cost["stone"]:
                return False
        if "iron" in resources_cost:
            if self.player_stats["Resources"]["iron"] < resources_cost["iron"]:
                return False
        if "gold" in resources_cost:
            if self.player_stats["Resources"]["gold"] < resources_cost["gold"]:
                return False
        if "diamond" in resources_cost:
            if self.player_stats["Resources"]["diamond"] < resources_cost["diamond"]:
                return False
        if "wood" in resources_cost:
            if self.player_stats["Resources"]["wood"] < resources_cost["wood"]:
                return False
            
        return True

    def add_trade_offer(self, resources_cost, resources_earned):
        #check if resources_earned and resources_cost are above 0
        for resource in resources_cost:
            if resources_cost[resource] < 0:
                print("resources_cost had a negative value: " +  str(resources_cost))
                return "resources_cost had a negative value" +  str(resources_cost)
        for resource in resources_earned:
            if resources_earned[resource] < 0:
                print("resources_earned had a negative value: " +  str(resources_cost))
                return "resources_earned had a negative value" +  str(resources_cost)
            
        #check market level and if there is an open spot (1 trade per market level)
        if self.player_stats["Buildings"]["levels"]["Market"] == 0:
            print("Market not built")
            return "Market not built"
        if len(self.player_stats["Market"]["listings"]) >= self.player_stats["Buildings"]["levels"]["Market"]:
            return "Max number of trades reached for Market level"
        
        #check if player has enough resources
        if not self.check_if_player_has_enough_resources(resources_cost):
            print("player does not have enough resources: " + str(resources_cost))
            return "player does not have enough resources: " + str(resources_cost)
        
        #subtract resources
        for resource in resources_cost:
            self.player_stats["Resources"][resource] -= resources_cost[resource]
        
        #add to market
        self.player_stats["Market"]["listings"].append({"resources_cost": resources_cost, "resources_earned": resources_earned})
        return "Success"
    
    def remove_trade_offer(self, trade_index):
        #check if trade_index is valid
        if trade_index >= len(self.player_stats["Market"]["listings"]):
            print("trade_index is invalid")
            return "Trade not found"
        
        
        

        # recover resources
        resources_cost = self.player_stats["Market"]["listings"][trade_index]["resources_cost"]
        for resource in resources_cost:
            self.player_stats["Resources"][resource] += resources_cost[resource]

        #remove trade
        self.player_stats["Market"]["listings"].pop(trade_index)

        return "Success"
    
    def accept_offer(self, trade_index, other_player = None):
        #recieve resources and remove trade

        resources_earned = self.player_stats["Market"]["listings"][trade_index]["resources_earned"]
        resources_cost = self.player_stats["Market"]["listings"][trade_index]["resources_cost"]
        
        #give resources to other player
        if other_player:
            #check if other player can make that trade
            if not other_player.trade_possible(resources_earned):
                print("not enough resources to make trade")
                return "not enough resources to make trade"

            #add resources to other player
            for resource in resources_cost:
                other_player.player_stats["Resources"][resource] += resources_cost[resource]
            
            #remove resources from other player
            for resource in resources_earned:
                other_player.player_stats["Resources"][resource] -= resources_earned[resource]

        for resource in resources_earned:
            self.player_stats["Resources"][resource] += resources_earned[resource]

        self.player_stats["Market"]["listings"].pop(trade_index)

        return "Success"