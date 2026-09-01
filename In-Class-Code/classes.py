class Animal:
    def __init__(self, name, age):
        self.name = name
        self.age = age
        
    def get_name(self):
        return self.name
    
    def get_age(self):
        return self.age
    
    def get_info(self):
        
        return f"Animal name: {self.name}\nAnimal age: {self.age}"
    
    
class Dog(Animal):
    def get_info(self):
        return f"Dog name: {self.name}\nDog age: {self.age}"
    
class Cat(Animal):
    def get_info(self):
        return f"Cat name: {self.name}\nCat age: {self.age}"
    
class Puppy(Dog):
    def get_info(self):
        return f"Puppy name: {self.name}\nPuppy age: {self.age}"    
    
    
    

animal = Animal("Rob", 12)
dog = Dog("Frank", 10)
cat = Cat("Sally", 8)
puppy = Puppy("cooper", 1)



print(dog.get_info())
print()
print(animal.get_info())
print()
print(cat.get_info())
print()
print(puppy.get_info())
print()
print(puppy.get_name())
print(puppy.get_age())