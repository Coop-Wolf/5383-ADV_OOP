from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import threading
import time

app = FastAPI()


# ============================================================
# FARMER CLASS
# ============================================================

class Farmer:

    def __init__(self, name, profit, cost):
        self.name = name
        self.lvl = 1
        self.profit = profit
        self.cost = cost
        self.costOfNextUpgrade = cost * 1.4

    def lvl_up(self):
        self.lvl += 1
        self.profit *= 1.25
        self.costOfNextUpgrade *= 1.5

    def show_cost(self):
        return self.cost


# ============================================================
# PLOW CLASS
# ============================================================

class Plow:

    def __init__(self, name, profit, cost):
        self.name = name
        self.lvl = 1
        self.profit = profit
        self.cost = cost
        self.costOfNextUpgrade = cost * 1.4

    def lvl_up(self):
        self.lvl += 1
        self.profit *= 1.25
        self.costOfNextUpgrade *= 1.5

    def show_cost(self):
        return self.cost



class Tractor:
    def __init__(self, name, profit, cost):
        self.name = name
        self.lvl = 1
        self.profit = profit
        self.cost = cost
        self.costOfNextUpgrade = cost * 1.4

    def lvl_up(self):
        self.lvl += 1
        self.profit *= 1.25
        self.costOfNextUpgrade *= 1.5

    def show_cost(self):
        return self.cost


class Harvester:
    def __init__(self, name, profit, cost):
        self.name = name
        self.lvl = 1
        self.profit = profit
        self.cost = cost
        self.costOfNextUpgrade = cost * 1.4

    def lvl_up(self):
        self.lvl += 1
        self.profit *= 1.25
        self.costOfNextUpgrade *= 1.5

    def show_cost(self):
        return self.cost


class CropDuster:
    def __init__(self, name, profit, cost):
        self.name = name
        self.lvl = 1
        self.profit = profit
        self.cost = cost
        self.costOfNextUpgrade = cost * 1.4

    def lvl_up(self):
        self.lvl += 1
        self.profit *= 1.25
        self.costOfNextUpgrade *= 1.5

    def show_cost(self):
        return self.cost


class Drone:
    def __init__(self, name, profit, cost):
        self.name = name
        self.lvl = 1
        self.profit = profit
        self.cost = cost
        self.costOfNextUpgrade = cost * 1.4

    def lvl_up(self):
        self.lvl += 1
        self.profit *= 1.25
        self.costOfNextUpgrade *= 1.5

    def show_cost(self):
        return self.cost


# ============================================================
# AVAILABLE FARMER TYPES
# ============================================================

farmer_types = [
    ("Basic Farmer", 1, 5),
    ("Skilled Farmer", 5, 25),
    ("Expert Farmer", 15, 75)
]


# ============================================================
# AVAILABLE PLOW TYPES
# ============================================================

plow_types = [
    ("Basic Plow", 3, 13),
    ("Heavy Plow", 10, 40),
    ("Industrial Plow", 30, 120)
]



tractor_types = [
    ("Basic Tractor", 15, 75),
    ("Heavy Tractor", 40, 200),
    ("Industrial Tractor", 100, 500)
]

harvester_types = [
    ("Basic Harvester", 50, 250),
    ("Advanced Harvester", 125, 625),
    ("Industrial Harvester", 300, 1500)
]

crop_duster_types = [
    ("Basic Crop Duster", 150, 750),
    ("Advanced Crop Duster", 375, 1875),
    ("Professional Crop Duster", 900, 4500)
]

drone_types = [
    ("Basic Drone", 400, 2000),
    ("Advanced Drone", 1000, 5000),
    ("Agricultural Drone", 2500, 12500)
]


# ============================================================
# PLAYER DATA
# ============================================================

farmers = [Farmer("Basic Farmer", 1, 5)]
plows = []

tractors = []
harvesters = []
crop_dusters = []
drones = []

money = 0
money_lock = threading.Lock()

MAX_EQUIPMENT = 6
MAX_LEVEL = 10

# Prestige
prestige_points = 0
PRESTIGE_REQUIREMENT = 100000
PRESTIGE_BONUS = 0.10


# Achievements

achievements = [
    {
        "id": "first_purchase",
        "name": "First Purchase",
        "description": "Buy your first piece of equipment.",
        "requirement": 1
    },
    {
        "id": "getting_started",
        "name": "Getting Started",
        "description": "Own 5 pieces of equipment.",
        "requirement": 5
    },
    {
        "id": "growing_farm",
        "name": "Growing Farm",
        "description": "Own 10 pieces of equipment.",
        "requirement": 10
    },
    {
        "id": "maxed_out",
        "name": "Maxed Out",
        "description": "Get an equipment item to level 10.",
        "requirement": 10
    },
    {
        "id": "big_money",
        "name": "Big Money",
        "description": "Reach $1,000.",
        "requirement": 1000
    },
    {
        "id": "millionaire",
        "name": "Millionaire",
        "description": "Reach $1,000,000.",
        "requirement": 1000000
    },
    {
        "id": "first_prestige",
        "name": "First Prestige",
        "description": "Prestige your farm for the first time.",
        "requirement": 1
    },
    {
        "id": "prestige_master",
        "name": "Prestige Master",
        "description": "Reach 5 prestige points.",
        "requirement": 5
    },
    {
        "id": "full_fleet",
        "name": "Full Fleet",
        "description": "Own 6 of every equipment type.",
        "requirement": 6
    }
]


# ============================================================
# GAME FUNCTIONS
# ============================================================

def generate_money():
    global money

    while True:
        time.sleep(1)

        with money_lock:

            total_profit = 0

            for f in farmers:
                total_profit += f.profit

            for p in plows:
                total_profit += p.profit

            for t in tractors:
                total_profit += t.profit

            for h in harvesters:
                total_profit += h.profit

            for c in crop_dusters:
                total_profit += c.profit

            for d in drones:
                total_profit += d.profit

            # Apply prestige bonus
            multiplier = 1 + (prestige_points * PRESTIGE_BONUS)

            money += total_profit * multiplier


money_thread = threading.Thread(target=generate_money)
money_thread.daemon = True
money_thread.start()



def get_total_profit():
    total = 0

    for f in farmers:
        total += f.profit

    for p in plows:
        total += p.profit

    for t in tractors:
        total += t.profit

    for h in harvesters:
        total += h.profit

    for c in crop_dusters:
        total += c.profit

    for d in drones:
        total += d.profit

    return total



def get_achievement_data():

    total_equipment = (
        len(farmers)
        + len(plows)
        + len(tractors)
        + len(harvesters)
        + len(crop_dusters)
        + len(drones)
    )

    all_equipment = (
        farmers
        + plows
        + tractors
        + harvesters
        + crop_dusters
        + drones
    )

    # Find the highest level of any equipment
    highest_level = 0

    for equipment in all_equipment:
        if equipment.lvl > highest_level:
            highest_level = equipment.lvl

    # Find the smallest equipment count
    # This determines progress toward owning
    # 6 of every equipment type
    full_fleet = min(
        len(farmers),
        len(plows),
        len(tractors),
        len(harvesters),
        len(crop_dusters),
        len(drones)
    )

    # Current progress for each achievement
    achievement_progress = {
        "first_purchase": total_equipment,
        "getting_started": total_equipment,
        "growing_farm": total_equipment,
        "maxed_out": highest_level,
        "big_money": money,
        "millionaire": money,
        "first_prestige": prestige_points,
        "prestige_master": prestige_points,
        "full_fleet": full_fleet
    }

    results = []

    # Build the data that will be sent to JavaScript
    for achievement in achievements:

        progress = achievement_progress[achievement["id"]]

        unlocked = progress >= achievement["requirement"]

        results.append({
            "id": achievement["id"],
            "name": achievement["name"],
            "description": achievement["description"],
            "progress": progress,
            "requirement": achievement["requirement"],
            "unlocked": unlocked
        })

    return results



# ============================================================
# WEB PAGE
# ============================================================

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


# ============================================================
# GAME STATE API
# ============================================================

@app.get("/game")
def game_state():
    with money_lock:
        return {
            "money": money,
            "income_per_second": get_total_profit() * (1 + (prestige_points * PRESTIGE_BONUS)),

            "prestige_points": prestige_points,
            "prestige_multiplier": 1 + (prestige_points * PRESTIGE_BONUS),
            "prestige_requirement": PRESTIGE_REQUIREMENT,

            "achievements": get_achievement_data(),

            "farmers": [
                {
                    "name": f.name,
                    "level": f.lvl,
                    "profit": f.profit,
                    "upgrade_cost": f.costOfNextUpgrade
                }
                for f in farmers
            ],

            "plows": [
                {
                    "name": p.name,
                    "level": p.lvl,
                    "profit": p.profit,
                    "upgrade_cost": p.costOfNextUpgrade
                }
                for p in plows
            ],
            
            "tractors": [
                {
                    "name": t.name,
                    "level": t.lvl,
                    "profit": t.profit,
                    "upgrade_cost": t.costOfNextUpgrade
                }
                for t in tractors
            ],

            "harvesters": [
                {
                    "name": h.name,
                    "level": h.lvl,
                    "profit": h.profit,
                    "upgrade_cost": h.costOfNextUpgrade
                }
                for h in harvesters
            ],

            "crop_dusters": [
                {
                    "name": c.name,
                    "level": c.lvl,
                    "profit": c.profit,
                    "upgrade_cost": c.costOfNextUpgrade
                }
                for c in crop_dusters
            ],

            "drones": [
                {
                    "name": d.name,
                    "level": d.lvl,
                    "profit": d.profit,
                    "upgrade_cost": d.costOfNextUpgrade
                }
                for d in drones
            ],

            "farmer_types": [
                {
                    "name": name,
                    "profit": profit,
                    "cost": cost
                }
                for name, profit, cost in farmer_types
            ],

            "plow_types": [
                {
                    "name": name,
                    "profit": profit,
                    "cost": cost
                }
                for name, profit, cost in plow_types
            ],
            
            "tractor_types": [
                {
                    "name": name,
                    "profit": profit,
                    "cost": cost
                }
                for name, profit, cost in tractor_types
            ],

            "harvester_types": [
                {
                    "name": name,
                    "profit": profit,
                    "cost": cost
                }
                for name, profit, cost in harvester_types
            ],

            "crop_duster_types": [
                {
                    "name": name,
                    "profit": profit,
                    "cost": cost
                }
                for name, profit, cost in crop_duster_types
            ],

            "drone_types": [
                {
                    "name": name,
                    "profit": profit,
                    "cost": cost
                }
                for name, profit, cost in drone_types
            ],
        }
    
@app.post("/buy/farmer/{farmer_index}")
def buy_farmer(farmer_index: int):
    global money

    if farmer_index < 0 or farmer_index >= len(farmer_types):
        return {
            "success": False,
            "message": "Invalid farmer."
        }

    name, profit, cost = farmer_types[farmer_index]

    with money_lock:

        if len(farmers) >= MAX_EQUIPMENT:
            return {
                "success": False,
                "message": "You can only own 5 farmers."
            }

        if money < cost:
            return {
                "success": False,
                "message": "Not enough money!"
            }

        money -= cost
        farmers.append(Farmer(name, profit, cost))

    return {
        "success": True,
        "message": f"Bought {name}!"
    }





@app.post("/buy/plow/{plow_index}")
def buy_plow(plow_index: int):
    global money

    if plow_index < 0 or plow_index >= len(plow_types):
        return {
            "success": False,
            "message": "Invalid plow."
        }

    name, profit, cost = plow_types[plow_index]

    with money_lock:

        if len(plows) >= MAX_EQUIPMENT:
            return {
                "success": False,
                "message": "You can only own 5 plows."
            }

        if money < cost:
            return {
                "success": False,
                "message": "Not enough money!"
            }

        money -= cost
        plows.append(Plow(name, profit, cost))

    return {
        "success": True,
        "message": f"Bought {name}!"
    }
    
    
@app.post("/buy/tractor/{tractor_index}")
def buy_tractor(tractor_index: int):
    global money

    if tractor_index < 0 or tractor_index >= len(tractor_types):
        return {
            "success": False,
            "message": "Invalid tractor."
        }

    name, profit, cost = tractor_types[tractor_index]

    with money_lock:

        if len(tractors) >= MAX_EQUIPMENT:
            return {
                "success": False,
                "message": "You can only own 5 tractors."
            }

        if money < cost:
            return {
                "success": False,
                "message": "Not enough money!"
            }

        money -= cost
        tractors.append(Tractor(name, profit, cost))

    return {
        "success": True,
        "message": f"Bought {name}!"
    }


@app.post("/buy/harvester/{harvester_index}")
def buy_harvester(harvester_index: int):
    global money

    if harvester_index < 0 or harvester_index >= len(harvester_types):
        return {
            "success": False,
            "message": "Invalid harvester."
        }

    name, profit, cost = harvester_types[harvester_index]

    with money_lock:

        if len(harvesters) >= MAX_EQUIPMENT:
            return {
                "success": False,
                "message": "You can only own 5 harvesters."
            }

        if money < cost:
            return {
                "success": False,
                "message": "Not enough money!"
            }

        money -= cost
        harvesters.append(Harvester(name, profit, cost))

    return {
        "success": True,
        "message": f"Bought {name}!"
    }


@app.post("/buy/crop-duster/{crop_duster_index}")
def buy_crop_duster(crop_duster_index: int):
    global money

    if crop_duster_index < 0 or crop_duster_index >= len(crop_duster_types):
        return {
            "success": False,
            "message": "Invalid crop duster."
        }

    name, profit, cost = crop_duster_types[crop_duster_index]

    with money_lock:

        if len(crop_dusters) >= MAX_EQUIPMENT:
            return {
                "success": False,
                "message": "You can only own 5 crop dusters."
            }

        if money < cost:
            return {
                "success": False,
                "message": "Not enough money!"
            }

        money -= cost
        crop_dusters.append(CropDuster(name, profit, cost))

    return {
        "success": True,
        "message": f"Bought {name}!"
    }


@app.post("/buy/drone/{drone_index}")
def buy_drone(drone_index: int):
    global money

    if drone_index < 0 or drone_index >= len(drone_types):
        return {
            "success": False,
            "message": "Invalid drone."
        }

    name, profit, cost = drone_types[drone_index]

    with money_lock:

        if len(drones) >= MAX_EQUIPMENT:
            return {
                "success": False,
                "message": "You can only own 5 drones."
            }

        if money < cost:
            return {
                "success": False,
                "message": "Not enough money!"
            }

        money -= cost
        drones.append(Drone(name, profit, cost))

    return {
        "success": True,
        "message": f"Bought {name}!"
    }
    
    
@app.post("/upgrade/farmer/{farmer_index}")
def upgrade_farmer(farmer_index: int):
    global money

    if farmer_index < 0 or farmer_index >= len(farmers):
        return {
            "success": False,
            "message": "That farmer doesn't exist."
        }

    with money_lock:
        farmer = farmers[farmer_index]

        if farmer.lvl >= MAX_LEVEL:
            return {
                "success": False,
                "message": "This farmer is already level 10."
            }

        if money < farmer.costOfNextUpgrade:
            return {
                "success": False,
                "message": "Not enough money!"
            }

        money -= farmer.costOfNextUpgrade
        farmer.lvl_up()

    return {
        "success": True,
        "message": f"{farmer.name} upgraded to level {farmer.lvl}!"
    }
    
    
    
    
    
@app.post("/upgrade/plow/{plow_index}")
def upgrade_plow(plow_index: int):
    global money

    if plow_index < 0 or plow_index >= len(plows):
        return {
            "success": False,
            "message": "That plow doesn't exist."
        }

    with money_lock:
        plow = plows[plow_index]

        if plow.lvl >= MAX_LEVEL:
            return {
                "success": False,
                "message": "This plow is already level 10."
            }

        if money < plow.costOfNextUpgrade:
            return {
                "success": False,
                "message": "Not enough money!"
            }

        money -= plow.costOfNextUpgrade
        plow.lvl_up()

    return {
        "success": True,
        "message": f"{plow.name} upgraded to level {plow.lvl}!"
    }
    
@app.post("/upgrade/tractor/{tractor_index}")
def upgrade_tractor(tractor_index: int):
    global money

    if tractor_index < 0 or tractor_index >= len(tractors):
        return {
            "success": False,
            "message": "That tractor doesn't exist."
        }

    with money_lock:
        tractor = tractors[tractor_index]

        if tractor.lvl >= MAX_LEVEL:
            return {
                "success": False,
                "message": "This tractor is already level 10."
            }

        if money < tractor.costOfNextUpgrade:
            return {
                "success": False,
                "message": "Not enough money!"
            }

        money -= tractor.costOfNextUpgrade
        tractor.lvl_up()

    return {
        "success": True,
        "message": f"{tractor.name} upgraded to level {tractor.lvl}!"
    }


@app.post("/upgrade/harvester/{harvester_index}")
def upgrade_harvester(harvester_index: int):
    global money

    if harvester_index < 0 or harvester_index >= len(harvesters):
        return {
            "success": False,
            "message": "That harvester doesn't exist."
        }

    with money_lock:
        harvester = harvesters[harvester_index]

        if harvester.lvl >= MAX_LEVEL:
            return {
                "success": False,
                "message": "This harvester is already level 10."
            }

        if money < harvester.costOfNextUpgrade:
            return {
                "success": False,
                "message": "Not enough money!"
            }

        money -= harvester.costOfNextUpgrade
        harvester.lvl_up()

    return {
        "success": True,
        "message": f"{harvester.name} upgraded to level {harvester.lvl}!"
    }


@app.post("/upgrade/crop-duster/{crop_duster_index}")
def upgrade_crop_duster(crop_duster_index: int):
    global money

    if crop_duster_index < 0 or crop_duster_index >= len(crop_dusters):
        return {
            "success": False,
            "message": "That crop duster doesn't exist."
        }

    with money_lock:
        crop_duster = crop_dusters[crop_duster_index]

        if crop_duster.lvl >= MAX_LEVEL:
            return {
                "success": False,
                "message": "This crop duster is already level 10."
            }

        if money < crop_duster.costOfNextUpgrade:
            return {
                "success": False,
                "message": "Not enough money!"
            }

        money -= crop_duster.costOfNextUpgrade
        crop_duster.lvl_up()

    return {
        "success": True,
        "message": f"{crop_duster.name} upgraded to level {crop_duster.lvl}!"
    }


@app.post("/upgrade/drone/{drone_index}")
def upgrade_drone(drone_index: int):
    global money

    if drone_index < 0 or drone_index >= len(drones):
        return {
            "success": False,
            "message": "That drone doesn't exist."
        }

    with money_lock:
        drone = drones[drone_index]

        if drone.lvl >= MAX_LEVEL:
            return {
                "success": False,
                "message": "This drone is already level 10."
            }

        if money < drone.costOfNextUpgrade:
            return {
                "success": False,
                "message": "Not enough money!"
            }

        money -= drone.costOfNextUpgrade
        drone.lvl_up()

    return {
        "success": True,
        "message": f"{drone.name} upgraded to level {drone.lvl}!"
    }
    
    
@app.post("/prestige")
def prestige():
    global money
    global prestige_points

    with money_lock:

        if money < PRESTIGE_REQUIREMENT:
            return {
                "success": False,
                "message": f"You need ${PRESTIGE_REQUIREMENT:,.0f} to prestige."
            }

        # Reset money
        money = 0

        # Reset all equipment
        farmers.clear()
        plows.clear()
        tractors.clear()
        harvesters.clear()
        crop_dusters.clear()
        drones.clear()

        # Give the player a starting farmer
        farmers.append(Farmer("Basic Farmer", 1, 5))

        # Give one prestige point
        prestige_points += 1

    return {
        "success": True,
        "message": "Prestige successful!",
        "prestige_points": prestige_points
    }
    

@app.get("/shop", response_class=HTMLResponse)
async def shop(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="shop.html"
    )


@app.get("/achievements", response_class=HTMLResponse)
async def achievements_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="achievements.html"
    )