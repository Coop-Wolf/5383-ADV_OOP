import requests
import time
from datetime import datetime

lat = 37.7749
lon = -122.4194
bearing = 90.0


data = {
    "id": "message",
    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "lat": lat,
    "lon": lon,
    "bearing": bearing,
}

while True:
    response = requests.post(
        "http://localhost:3000/api/write_gps",
        json=data
    )

    print(response.text)
    
    time.sleep(1)