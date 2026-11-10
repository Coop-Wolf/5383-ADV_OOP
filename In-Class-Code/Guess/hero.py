import requests

url = "http://localhost:5000/api/guess_number"

while True:
    try:
        number = int(input("Enter your guess: "))
    except ValueError:
        print("Please enter a whole number.")
        continue

    response = requests.post(url, json={"number": number})
    data = response.json()

    if response.status_code != 200:
        print(data.get("error"))
        break

    print(data["result"])
    if data.get("message"):
        print(data["message"])
    if data["game_over"]:
        break
    print(f"{data['tries_left']} tries left")