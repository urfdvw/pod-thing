# SPDX-FileCopyrightText: 2020 Brent Rubell for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import ipaddress
import ssl
import wifi
import socketpool
import adafruit_requests

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
#%%
pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())
#%% next track
requests.post(
    "https://api.spotify.com/v1/me/player/next",
    headers = {
        "Authorization": "Bearer BQC5Koasb10Z3zdTJLSB7brjhgPJX_J0W-w4UvUmagT4miOT9Cxh3XVFJ9N7lGV6Z69DHV4j9ZTEGqQi3OxyvvbEpDIiOP3kYx_MQAdpG8gtb0rbcWK6JI1Q1j8sUkWZFOKnjVJ48yLecC39_qxAU0gJQ_g1Kn6SxKmSHF9fNBvj4ZIduYZdy0dXidUPp-zAKLTseFc",
        "Content-Type": "application/json",
        "Accept": "application/json"
    },
    json = {}
)
#%% user
response = requests.get(
    "https://accounts.spotify.com/api/token",
    headers = {
        "Authorization": "Basic " + secrets['spotify_client_id'] + ':' + secrets['spotify_client_secret'],
        "Content-Type": "application/json",
        "Accept": "application/json"
    },
    json = {
        "grant_type": "client_credentials"
    }
)
print('-' * 20)
print(response.content)