# creating template for employee name and salary
employee = [{"name": "", "salary": 0}]

def add_employee(name, salary):
    employee.append({"name" : name, "salary": salary})
    
add_employee("cooper", 12)
print(employee)