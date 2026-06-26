import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from datetime import datetime

MQTT_HOST = "localhost"
SCHEDULE_TOPIC = "energy/tomorrow/schedule"
SONOFF_TOPIC = "cmnd/sonoff/POWER"

schedule = [0] * 96

def on_message(client, userdata, msg):
    global schedule
    payload = msg.payload.decode()
    schedule = [int(x) for x in payload.split(",")]
    print("Updated schedule")

client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_HOST)
client.subscribe(SCHEDULE_TOPIC)
client.loop_start()

def get_quarter_index():
    now = datetime.now()
    return now.hour * 4 + now.minute // 15

while True:
    idx = get_quarter_index()
    state = "ON" if schedule[idx] == 1 else "OFF"
    publish.single(SONOFF_TOPIC, state, hostname=MQTT_HOST)
    time.sleep(60)  # check once per minute
