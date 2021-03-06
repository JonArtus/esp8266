import ujson
from machine import Pin, Timer
from secret import wifi, mqtt, client_id
from config import config

print('Setting up config for Client ID %s' % (client_id))
conf = config[client_id]
print(ujson.dumps(conf))

leds = { }

for led in conf['leds']:
  print(led)
  pin = conf['leds'][led]
  print('Initialising led %s on pin %s' % (led, pin))
  leds[led] = Pin(pin, Pin.OUT)

heartbeat_payload = {
  'client_id': client_id,
  'freq': machine.freq(),
  'heartbeat_count': 0
}

def sub_cb(topic, msg):
  print((topic, msg))
  
  if topic == b'admin':
    if msg == b'reset': 
      print('Restarting due to admin request...')
      machine.reset()    
      
  if topic == b'led':
    inst = ujson.loads(msg.decode('ascii'))
    leds[inst['name']].value(inst['value'])   
 
def publish_heartbeat(client):
  heartbeat_payload['heartbeat_count'] = heartbeat_payload['heartbeat_count'] + 1
  client.publish('heartbeat', ujson.dumps(heartbeat_payload))
  
def connect_and_subscribe():  
  client = MQTTClient(client_id, mqtt['server'], user=mqtt['user'], password=mqtt['pass'])
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(b'led')
  client.subscribe(b'admin')
  print('Connected to %s MQTT broker, subscribed to topics' % (mqtt['server']))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

tim = Timer(-1)
tim.init(period=5000, mode=Timer.PERIODIC, callback=lambda _: publish_heartbeat(client))

while True:
  try:
    client.check_msg()
  except OSError as e:
    restart_and_reconnect()

