from machine import Pin
from secret import mqtt

led = Pin(2, Pin.OUT)

def sub_cb(topic, msg):
  print((topic, msg))
  
  if topic == b'admin':
    if msg == b'reset': 
      print('Restarting due to admin request...')
      machine.reset()
  
  if topic == b'led' and msg == b'on':
    led.value(False)
  if topic == b'led' and msg == b'off':
    led.value(True)
 
  
def connect_and_subscribe():
  global client_id, mqtt['server'], mqtt['user'], mqtt['pass'], topic_sub
  client = MQTTClient(client_id, mqtt_server, user=mqtt_user, password=mqtt_pass)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(b'led')
  client.subscribe(b'admin')
  print('Connected to %s MQTT broker, subscribed to topics' % (mqtt_server))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    client.wait_msg()
  except OSError as e:
    restart_and_reconnect()

