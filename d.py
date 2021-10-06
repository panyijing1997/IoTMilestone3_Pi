import json
import ssl
import time

import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
    else:
        print("Connect returned result code: " + str(rc))

def on_disconnect(client, userdata, rc):
    print("disconnected, but will reconnect")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("Received message: " + msg.topic + " -> " + msg.payload.decode("utf-8"))

# create the client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect=on_disconnect

# enable TLS
client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS,cert_reqs=ssl.CERT_NONE)

# set username and password

client.username_pw_set("sensor", "Nishishabi123")

# connect to HiveMQ Cloud on port 8883
client.connect("4ff8e85e4274405ab458c0d0e8430b63.s1.eu.hivemq.cloud", 8883)

# subscribe to the topic "my/test/topic"
client.subscribe("my/test/topic")

# publish "Hello" to the topic "my/test/topic"

client.publish("queen/dht11",json.dumps({"msg":"DFDD", "temperature":4588787875, "humidity":123}))

# Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
client.loop_start()
while True:
    client.publish("my/test/topic", "Hello")
    time.sleep(2)