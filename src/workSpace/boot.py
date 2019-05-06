import time
import ubinascii
import machine
import micropython
import network
import esp
import gc

from umqttsimple import MQTTClient
from secret import wifi, client_id

esp.osdebug(None)
gc.collect()

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(wifi['ssid'], wifi['pass'])

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())

