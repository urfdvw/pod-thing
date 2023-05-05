# SPDX-FileCopyrightText: 2020 Brent Rubell for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import ipaddress
import ssl
import wifi
import socketpool
import adafruit_requests

# URLs to fetch from
TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"
JSON_QUOTES_URL = "https://www.adafruit.com/api/quotes.php"
JSON_STARS_URL = "https://api.github.com/repos/adafruit/circuitpython"

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

print("ESP32-S2 WebClient Test")

print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])

print("Available WiFi networks:")
for network in wifi.radio.start_scanning_networks():
    print("\t%s\t\tRSSI: %d\tChannel: %d" % (str(network.ssid, "utf-8"),
            network.rssi, network.channel))
wifi.radio.stop_scanning_networks()

print("Connecting to %s"%secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!"%secrets["ssid"])
print("My IP address is", wifi.radio.ipv4_address)

ipv4 = ipaddress.ip_address("8.8.4.4")
print("Ping google.com: %f ms" % (wifi.radio.ping(ipv4)*1000))

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())



SPOTIFY_CREATE_PLAYLIST_URL = 'https://api.spotify.com/v1/users/y00thocyh8pfmsszb17ux5om5/playlists'
TOKEN = 'BQDYyFwGx0HARSijIsnBcciXMB_Bl7yHtNDuJWisFHYbyi1eAPjfknEq7f-vthrztstMwLJDBhQai2V8tFZ0xdzhzbpv6DJ2I3VfHTElNm3iU9P3lktFRv7F_md3kZGlRKWI_UajUzKfXXNHosIlTPi8-BsNAwBBHg3MFE6Z0Y7VYEurR6JiXIYxUd3mA9JZY4XOf1PYP5L8PaC9jIUSN3mPLUeMlrvF3tDwoOE04mEsOLvG4gp27zcyhoerxiiG'

response = requests.post(
    SPOTIFY_CREATE_PLAYLIST_URL,
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    },
    json={
        "name": "ESP32S2",
        "public": False
    }
)

print(response.json())