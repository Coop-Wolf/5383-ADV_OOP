import os

class Util():
    @staticmethod
    def clear_screen():
        os.system("cls" if os.name == "nt" else "clear")
        
    @staticmethod
    def ask_yes_no(prompt):
        """Returns True for 'y', False for 'n', None if input was interrupted."""
        while True:
            try:
                choice = input(prompt).strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nInput interrupted. Exiting game.")
                return None

            if choice in ("y", "n"):
                return choice == "y"
            print("ERROR: please enter 'y' or 'n'.")

    @staticmethod
    def ask_int(prompt, minimum=None, maximum=None):
        """Keeps asking until the user enters a whole number in range."""
        while True:
            try:
                value = int(input(prompt))
            except ValueError:
                print("  ERROR: Please enter a valid number.")
                continue

            if minimum is not None and value < minimum:
                print(f"  ERROR: Must be at least {minimum}.")
            elif maximum is not None and value > maximum:
                print(f"  ERROR: Must be at most {maximum}.")
            else:
                return value

    @staticmethod
    def banner(title, width=50):
        print()
        print("=" * width)
        print(title.center(width))
        print("=" * width)
        print()