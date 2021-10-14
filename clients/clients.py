import json

import RPi.GPIO as GPIO
import board
import adafruit_dht
import time
import ssl
import paho.mqtt.client as mqtt
import socket

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# set ports for LEDs
GPIO.setup(4, GPIO.OUT)  # set #4 as ouput port
GPIO.output(4, GPIO.LOW)  # initially turned off
GPIO.setup(2, GPIO.OUT)
GPIO.output(2, GPIO.LOW)
GPIO.setup(22, GPIO.OUT)
GPIO.output(22, GPIO.LOW)

# set ports for distance sensor
TRIG = 23
ECHO = 24
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)



"""
mqtt functions for server
"""
def on_disconnect(client, userdata, rc):
    print("disconnected, but will reconnect")
    client.reconnect()


def on_subscribe_led(client, userdata, mid, granted_qos):
    print("led subscribed")
    print(granted_qos)

def on_connect_led(client, userdata, flags, rc):
    print(f"leds connected with result code {rc}")
    client.subscribe("queen/led/action",1)
    client.subscribe("check_led",1)

def on_connect_led_cloud(client, userdata, flags, rc):
    print(f"leds connected with result code {rc}")
    client.subscribe("check_led", 1)

# when LED receives message of changing states
def on_message_led(client, userdata, message):
    print(f"led receivedd a message")
    if message.topic == "check_led":
        ledState_blue = GPIO.input(4)
        ledState_red = GPIO.input(2)
        ledState_green = GPIO.input(22)
        ledState = {
            'led_blue': ledState_blue,
            'led_red': ledState_red,
            'led_green': ledState_green,
        }
        client.publish("queen/led/state", json.dumps(ledState))
    elif message.topic == "queen/led/action":
        msg=str(message.payload.decode("utf-8"))
        msg=json.loads(msg)
        print(msg)
        if msg['color']=="blue":
            if msg['action']=="on":
                GPIO.output(4, GPIO.HIGH)
            else:
                GPIO.output(4, GPIO.LOW)
        elif msg['color']=="green":
            if msg['action'] == "on":
                GPIO.output(22, GPIO.HIGH)
            else:
                GPIO.output(22, GPIO.LOW)
        elif msg['color']=="red":
            if msg['action']=="on":
                GPIO.output(2, GPIO.HIGH)
            else:
                GPIO.output(2, GPIO.LOW)

        # after change publish state:
        ledState_blue = GPIO.input(4)
        ledState_red = GPIO.input(2)
        ledState_green = GPIO.input(22)
        ledState = {
            'led_blue': ledState_blue,
            'led_red': ledState_red,
            'led_green': ledState_green,
        }
        client.publish("queen/led/state",json.dumps(ledState))
        cloud_ledc.publish("queen/led/state", json.dumps(ledState))

    else:
        print(str(message.payload.decode("utf-8")))

def on_connect_sensort(client, userdata, flags, rc):
    print(f"dht11 client Connected with result code {rc}")
    client.subscribe("queen/dht11_check")

def on_message_sensort(client, userdata, message):
    r_msg=str(message.payload.decode("utf-8"))
    print("temp received check")

    dhtDevice = adafruit_dht.DHT11(board.D12, use_pulseio=False)
    try:
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity
        if humidity is not None and temperature is not None:
            msg = "read from the sensor successfully"
            templateData = {
                'temperature': temperature,
                'humidity': humidity,
                'msg': msg
            }
        client.publish("queen/dht11_store",json.dumps(templateData))
    except RuntimeError as error:
        client.publish("queen/dht11_error", "read_failed")
        dhtDevice.exit()

    except Exception as error:
        client.publish("queen/dht11_error", "read_failed")
        dhtDevice.exit()

def on_connect_sensord(client, userdata, flags, rc):
    print(f"distance measure client Connected with result code {rc}")
    client.subscribe("queen/distance_check")

def on_publish_sensord(client, userdata, mid):
    print("distance data published")

def on_message_sensord(client, userdata, message):
    print(f"distance sensor receivedd a message")
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start = 0
    pulse_end = 0

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    templateData = {
        'dist': distance,
    }
    #client.publish("queen/distance", json.dumps(templateData), retain=True)
    client.publish("queen/distance_store", json.dumps(templateData))
    print(templateData)


##connect to local broker
ledc = mqtt.Client()
ledc.on_disconnect= on_disconnect
ledc.on_connect = on_connect_led
ledc.on_message = on_message_led
ledc.username_pw_set("local","shuihouzishuihouzi")
ledc.on_subscribe=on_subscribe_led
ledc.connect("mosquitto", 1883, 200)
ledc.loop_start()


sensord=mqtt.Client()
sensord.on_disconnect= on_disconnect
sensord.on_connect=on_connect_sensord
sensord.on_publish=on_publish_sensord
sensord.on_message=on_message_sensord
sensord.username_pw_set("local","shuihouzishuihouzi")
sensord.connect("mosquitto", 1883, 200)
sensord.loop_start()

sensort=mqtt.Client()
sensort.on_disconnect= on_disconnect
sensort.on_connect=on_connect_sensort
sensort.on_message=on_message_sensort
sensort.username_pw_set("local","shuihouzishuihouzi")
sensort.connect("mosquitto", 1883, 200)
sensort.loop_start()

ledc.publish("test","sdfgdsdfg")


##connect to cloud broker
cloud_ledc = mqtt.Client()
cloud_ledc.on_disconnect= on_disconnect
cloud_ledc.on_connect = on_connect_led_cloud
cloud_ledc.on_message = on_message_led
cloud_ledc.on_subscribe=on_subscribe_led
cloud_ledc.username_pw_set("sensor","Nishishabi123")
cloud_ledc.connect("4ff8e85e4274405ab458c0d0e8430b63.s1.eu.hivemq.cloud", 8883, 200)
cloud_ledc.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS,cert_reqs=ssl.CERT_NONE)
cloud_ledc.loop_start()


cloud_sensord=mqtt.Client()
cloud_sensord.on_disconnect= on_disconnect
cloud_sensord.on_connect=on_connect_sensord
cloud_sensord.on_publish=on_publish_sensord
cloud_sensord.on_message=on_message_sensord
cloud_sensord.username_pw_set("sensor","Nishishabi123")
cloud_sensord.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS,cert_reqs=ssl.CERT_NONE)
cloud_sensord.connect("4ff8e85e4274405ab458c0d0e8430b63.s1.eu.hivemq.cloud", 8883, 200)
cloud_sensord.loop_start()

cloud_sensort=mqtt.Client()
cloud_sensort.on_disconnect= on_disconnect
cloud_sensort.on_connect=on_connect_sensort
cloud_sensort.on_message=on_message_sensort
cloud_sensort.username_pw_set("sensor","Nishishabi123")
cloud_sensort.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS,cert_reqs=ssl.CERT_NONE)
cloud_sensort.connect("4ff8e85e4274405ab458c0d0e8430b63.s1.eu.hivemq.cloud", 8883, 200)
cloud_sensort.loop_start()


while True:
    print("interval-------")
    # periodically send temperature and humidity measured data to broker
    dhtDevice = adafruit_dht.DHT11(board.D12, use_pulseio=False)
    try:
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity
        if humidity is not None and temperature is not None:
            msg = "read from the sensor successfully"
            templateData = {
                'temperature': temperature,
                'humidity': humidity,
                'msg': msg
            }
        print("temp read successed (perioddical reading)")
        sensort.publish("queen/dht11_store",json.dumps(templateData))
        cloud_sensort.publish("queen/dht11_store", json.dumps(templateData))
    except RuntimeError as error:
        sensort.publish("queen/dht11_error", "read_failed")
        cloud_sensort.publish("queen/dht11_error", "read_failed")
        print("temp read failed (perioddical reading)")
        dhtDevice.exit()

    except Exception as error:
        cloud_sensort.publish("queen/dht11_error", "read_failed")
        sensort.publish("queen/dht11_error", "read_failed")
        print("temp read failed (perioddical reading)")
        dhtDevice.exit()

    # periodically send distance measured data to broker
#     GPIO.output(TRIG, True)
#     time.sleep(0.00001)
#     GPIO.output(TRIG, False)
#     pulse_start = 0
#     pulse_end = 0
#     while GPIO.input(ECHO) == 0:
#         pulse_start = time.time()
#     while GPIO.input(ECHO) == 1:
#         pulse_end = time.time()
#     pulse_duration = pulse_end - pulse_start
#     distance = pulse_duration * 17150
#     distance = round(distance, 2)
#     templateData = {
#         'dist': distance,
#     }
#     #client.publish("queen/distance", json.dumps(templateData), retain=True)
#     sensord.publish("queen/distance_store", json.dumps(templateData))
#     cloud_sensord.publish("queen/distance_store", json.dumps(templateData))


    time.sleep(10)
