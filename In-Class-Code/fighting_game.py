import time

class Champion:
    def __init__(self, name, attack, health, s_attack, heal):
        self.name = name
        self._attack = attack
        self.health = health
        self.s_attack = s_attack
        self._heal = heal

    def get_info(self):
        return f"Name: {self.name}\nAttack: {self._attack}\nHealth: {self.health}\nSpecial Attack: {self.s_attack}\nHeal: {self._heal}"

    def get_name(self):
        return self.name

    def take_damage(self, damage):
        self.health -= damage

    def attack(self):
        return self._attack

    def heal(self):
        self.health += self._heal

    def is_alive(self):
        return self.health > 0
    
    def special_attack(self):
        return self.s_attack


class Spartan(Champion):
    def __init__(self):
        super().__init__("Spartan", 21, 120, 42, 15)

class Orc(Champion):
    def __init__(self):
        super().__init__("Orc", 18, 140, 35, 10)

class Pirate(Champion):
    def __init__(self):
        super().__init__("Pirate", 19, 110, 38, 12)

class Dragon(Champion):
    def __init__(self):
        super().__init__("Dragon", 25, 160, 50, 10)

class Wizard(Champion):
    def __init__(self):
        super().__init__("Wizard", 15, 90, 55, 20)

class Ninja(Champion):
    def __init__(self):
        super().__init__("Ninja", 23, 95, 45, 13)

class Knight(Champion):
    def __init__(self):
        super().__init__("Knight", 20, 135, 36, 16)


class Game:
    def __init__(self, champions):
        self.champions = champions
        self.player1 = None
        self.player2 = None
        print("Welcome to Cooper's fighting game!")

    def show_champion_list(self):
        print("\nAvailable Champions:")
        for i, champ in enumerate(self.champions, start=1):
            print(f"  {i}. {champ.get_name()}")

    def choose_champion(self, player_label):
        self.show_champion_list()
        while True:
            choice = input(f"{player_label}, choose your champion (enter number): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(self.champions):
                index = int(choice) - 1
                selected = self.champions[index]

                # Remove selected champion from list so the other player can't pick it
                self.champions.pop(index)

                # Return a fresh Champion instance so both players don't share/modify the same object
                return Champion(selected.name, selected._attack, selected.health, selected.s_attack, selected._heal)
            print("Invalid choice, try again.")

    def game_info(self, player1, player2):
        return player1.get_info() + "\n\n" + player2.get_info()

    def action_option(self, player):
        print(f"\n{player.get_name()}'s turn:")
        print("  1. Attack")
        print("  2. Heal")
        print("  3. Special Attack")
        while True:
            choice = input("Choose an action (enter number): ").strip()
            if choice == "1":
                return "attack"
            elif choice == "2":
                return "heal"
            elif choice == "3":
                return "special"
            print("Invalid choice, try again.")

    def start(self):
        self.player1 = self.choose_champion("Player 1")
        self.player2 = self.choose_champion("Player 2")

        print()
        print(f"Matchup: {self.player1.get_name()} vs {self.player2.get_name()}")
        print()

        round_num = 1
        while True:
            print(f"--- Round {round_num} ---")

            action1 = self.action_option(self.player1)

            if action1 == "attack":
                self.player2.take_damage(self.player1.attack())
                print(f"{self.player1.get_name()} attacks {self.player2.get_name()}!")
            elif action1 == "special":
                self.player2.take_damage(self.player1.special_attack())
                print(f"{self.player1.get_name()} unleashes a special attack on {self.player2.get_name()}!")
            else:
                self.player1.heal()
                print(f"{self.player1.get_name()} heals!")

            if not self.player2.is_alive():
                print(f"{self.player2.get_name()} has been defeated!")
                break

            action2 = self.action_option(self.player2)

            if action2 == "attack":
                self.player1.take_damage(self.player2.attack())
                print(f"{self.player2.get_name()} attacks {self.player1.get_name()}!")
            elif action2 == "special":
                self.player1.take_damage(self.player2.special_attack())
                print(f"{self.player2.get_name()} unleashes a special attack on {self.player1.get_name()}!")
            else:
                self.player2.heal()
                print(f"{self.player2.get_name()} heals!")

            if not self.player1.is_alive():
                print(f"{self.player1.get_name()} has been defeated!")
                break

            print()
            print(self.game_info(self.player1, self.player2))
            print()
            round_num += 1
            time.sleep(0.5)

        if self.player1.is_alive():
            print(f"{self.player1.get_name()} wins!")
        else:
            print(f"{self.player2.get_name()} wins!")


champions = [
    Spartan(),
    Orc(),
    Pirate(),
    Dragon(),
    Wizard(),
    Ninja(),
    Knight(),
]

game = Game(champions)
game.start()