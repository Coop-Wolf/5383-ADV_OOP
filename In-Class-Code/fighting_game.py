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


class Game:
    def __init__(self, champions):
        self.champions = champions
        print("Welcome to Cooper's game!")

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


def get_player1_action(player1):
    while True:
        choice = input(f"Player 1 ({player1.get_name()}): [a]ttack or [h]eal? ").strip().lower()
        if choice in ("a", "h"):
            return "attack" if choice == "a" else "heal"
        print("Invalid input, try again.")


def get_player2_action(player2):
    while True:
        choice = input(f"Player 2 ({player2.get_name()}): [a]ttack or [h]eal? ").strip().lower()
        if choice in ("a", "h"):
            return "attack" if choice == "a" else "heal"
        print("Invalid input, try again.")


# Master roster — the "template" champions players pick from
champions = [
    Champion("Spartan", 21, 120, 42, 15),
    Champion("Orc", 18, 140, 35, 10),
    Champion("Pirate", 19, 110, 38, 12),
    Champion("Dragon", 25, 160, 50, 10),
    Champion("Wizard", 15, 90, 55, 20),
    Champion("Ninja", 23, 95, 45, 13),
    Champion("Knight", 20, 135, 36, 16),
]

game = Game(champions)

player1 = game.choose_champion("Player 1")
player2 = game.choose_champion("Player 2")

print()
print(f"Matchup: {player1.get_name()} vs {player2.get_name()}")
print()

round_num = 1
while player1.is_alive() and player2.is_alive():
    print(f"--- Round {round_num} ---")

    action1 = get_player1_action(player1)
    action2 = get_player2_action(player2)

    if action1 == "attack":
        player2.take_damage(player1.attack())
        print(f"{player1.get_name()} attacks {player2.get_name()}!")
    else:
        player1.heal()
        print(f"{player1.get_name()} heals!")

    if action2 == "attack":
        player1.take_damage(player2.attack())
        print(f"{player2.get_name()} attacks {player1.get_name()}!")
    else:
        player2.heal()
        print(f"{player2.get_name()} heals!")

    print()
    print(game.game_info(player1, player2))
    print()
    round_num += 1
    time.sleep(0.5)



if player1.is_alive():
    print(f"{player1.get_name()} wins!")
else:
    print(f"{player2.get_name()} wins!")