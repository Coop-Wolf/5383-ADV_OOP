import time
import threading


class farmer:
    def __init__(self):
        self.lvl = 1
        self.profit = 1
        self.cost = 5
        self.costOfNextUpgrade = 7

    def lvl_up(self):
        self.lvl += 1
        self.profit *= 1.25
        self.costOfNextUpgrade *= 1.5

    def show_cost(self):
        return self.cost


class plow:
    def __init__(self):
        self.lvl = 1
        self.profit = 3
        self.cost = 13
        self.costOfNextUpgrade = 20

    def lvl_up(self):
        self.lvl += 1
        self.profit *= 1.25
        self.costOfNextUpgrade *= 1.5

    def show_cost(self):
        return self.cost


def generate_money():
    global money

    while True:
        time.sleep(1)

        for f in farmers:
            money += f.profit

        for p in plows:
            money += p.profit


farmers = [farmer()]
plows = []

exampleplow = plow()

money = 0


# Start money generation in a separate thread
money_thread = threading.Thread(target=generate_money)
money_thread.daemon = True
money_thread.start()


# Display menu
print(f"1. Buy Farmer (${farmers[0].show_cost():.2f})")
print(f"2. Buy Plow (${exampleplow.show_cost():.2f})")
print("1.x Upgrade Farmer")
print("2.x Upgrade Plow")
print("3. Show Stats")


while True:

    # Wait for player input while money continues generating
    choice = input("Choice: ")

    if choice == "1":
        new_farmer = farmer()

        if money >= new_farmer.cost:
            money -= new_farmer.cost
            farmers.append(new_farmer)
            print("Bought a farmer!")
        else:
            print("Not enough money!")

    elif choice.startswith("1."):
        index = int(choice[2:]) - 1

        if index < len(farmers):
            f = farmers[index]

            if money >= f.costOfNextUpgrade:
                money -= f.costOfNextUpgrade
                f.lvl_up()
                print("Farmer upgraded!")
            else:
                print("Not enough money!")
        else:
            print("That farmer doesn't exist.")

    elif choice == "2":
        new_plow = plow()

        if money >= new_plow.cost:
            money -= new_plow.cost
            plows.append(new_plow)
            print("Bought a plow!")
        else:
            print("Not enough money!")

    elif choice.startswith("2."):
        index = int(choice[2:]) - 1

        if index < len(plows):
            p = plows[index]

            if money >= p.costOfNextUpgrade:
                money -= p.costOfNextUpgrade
                p.lvl_up()
                print("Plow upgraded!")
            else:
                print("Not enough money!")
        else:
            print("That plow doesn't exist.")

    elif choice == "3":
        print("==================================================================================")
        print()
        print(f"Money: ${money:.2f}")

        total_profit = sum(f.profit for f in farmers) + sum(p.profit for p in plows)
        print(f"Income per second: ${total_profit:.2f}")

        print()
        print("FARMERS")

        for i, f in enumerate(farmers):
            print(
                f"  Farmer {i + 1}: Level {f.lvl} | "
                f"Profit: ${f.profit:.2f}/sec | "
                f"Upgrade: ${f.costOfNextUpgrade:.2f}"
            )

        print()
        print("PLOWS")

        for i, p in enumerate(plows):
            print(
                f"  Plow {i + 1}: Level {p.lvl} | "
                f"Profit: ${p.profit:.2f}/sec | "
                f"Upgrade: ${p.costOfNextUpgrade:.2f}"
            )

        print()
        print("==================================================================================")
        print()