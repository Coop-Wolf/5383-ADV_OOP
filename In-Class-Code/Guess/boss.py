import requests

url = "http://localhost:5000/api/set_number"

number = int(input("Enter a number between 1 and 100: "))

response = requests.post(url, json={"number": number})



print(response.json())