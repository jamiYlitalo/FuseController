import requests
import paho.mqtt.publish as publish
from datetime import datetime, timedelta

API_URL = "https://api.porssisahko.net/v2/latest-prices.json"
MQTT_HOST = "192.168.1.50"
MQTT_TOPIC = "energy/tomorrow/schedule"

HOURS_ON = 6

def get_tomorrow_prices():
    r = requests.get(API_URL)
    data = r.json()

    now = datetime.now()
    tomorrow = (now + timedelta(days=1)).date()

    entries = []
    for entry in data["prices"]:
        start = datetime.fromisoformat(entry["startDate"].replace("Z", "+00:00")).astimezone()
        if start.date() == tomorrow:
            entries.append((start, entry["price"]))

    entries.sort(key=lambda x: x[0])
    return entries  # list of (timestamp, price)

def compute_schedule(entries):
    # entries = 96 quarter-hours
    prices = [p for (_, p) in entries]

    # Find cheapest N quarter-hours
    n = HOURS_ON * 4
    cheapest_indices = sorted(range(96), key=lambda i: prices[i])[:n]

    schedule = [0] * 96
    for i in cheapest_indices:
        schedule[i] = 1  # 1 = ON, 0 = OFF

    return schedule

def publish_schedule(schedule):
    payload = ",".join(str(x) for x in schedule)
    publish.single(MQTT_TOPIC, payload, hostname=MQTT_HOST)
    print("Published schedule")

if __name__ == "__main__":
    entries = get_tomorrow_prices()
    schedule = compute_schedule(entries)
    publish_schedule(schedule)
