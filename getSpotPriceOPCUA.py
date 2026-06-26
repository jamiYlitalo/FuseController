from opcua import ua, Server
import requests
from datetime import datetime, timedelta

API_URL = "https://api.porssisahko.net/v2/latest-prices.json"

def get_tomorrow_prices():
    r = requests.get(API_URL)
    data = r.json()

    now_local = datetime.now()
    tomorrow = (now_local + timedelta(days=1)).date()

    prices = []

    for entry in data["prices"]:
        start_utc = datetime.fromisoformat(entry["startDate"].replace("Z", "+00:00"))
        start_local = start_utc.astimezone()

        if start_local.date() == tomorrow:
            prices.append((start_local, entry["price"]))

    prices.sort(key=lambda x: x[0])

    # Extract only price values
    return [p[1] for p in prices]

# --- OPC UA Server ---
server = Server()
server.set_endpoint("opc.tcp://0.0.0.0:4840/")

objects = server.get_objects_node()

# Create an array variable of 96 doubles
price_array = objects.add_variable(
    "ns=2;s=TomorrowPrices",
    "TomorrowPrices",
    [0.0] * 96,
    varianttype=ua.VariantType.Double
)
price_array.set_writable()

server.start()
print("OPC UA server running...")

while True:
    prices = get_tomorrow_prices()

    if len(prices) == 96:
        price_array.set_value(ua.Variant(prices, ua.VariantType.Double))
        print("Updated tomorrow price curve")
    else:
        print("Warning: expected 96 values, got", len(prices))

    time.sleep(300)  # update every 5 minutes
