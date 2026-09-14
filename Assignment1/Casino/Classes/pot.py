class Pot:
    def __init__(self):
        self.amount = 0

    def add(self, amount):
        self.amount += amount

    def collect(self):
        return self.amount