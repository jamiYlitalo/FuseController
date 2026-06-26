import requests
import paho.mqtt.publish as publish
from datetime import datetime, timedelta

API_URL = "https://api.porssisahko.net/v2/latest-prices.json"
MQTT_HOST = "192.168.1.50"   # Raspberry Pi IP
MQTT_TOPIC = "cmnd/sonoff/POWER"  # Tasmota command topic

CHEAP_THRESHOLD = 3.0

def get_current_price():
    r = requests.get(API_URL)
    data = r.json()

    now = datetime.now().astimezone()

    for entry in data["prices"]:
        start = datetime.fromisoformat(entry["startDate"].replace("Z", "+00:00")).astimezone()
        end = datetime.fromisoformat(entry["endDate"].replace("Z", "+00:00")).astimezone()

        if start <= now <= end:
            return entry["price"]

    return None

def control_sonoff(price):
    if price < CHEAP_THRESHOLD:
        publish.single(MQTT_TOPIC, "ON", hostname=MQTT_HOST)
        print("Cheap → turning ON")
    else:
        publish.single(MQTT_TOPIC, "OFF", hostname=MQTT_HOST)
        print("Expensive → turning OFF")

if __name__ == "__main__":
    price = get_current_price()
    print("Current price:", price)
    control_sonoff(price)
