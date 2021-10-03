import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

def on_connect(client, userdata, flags,  rc):
    print(f"Connected with result code{rc}")
    client.subscribe("topic/led")

def on_message(client, userdata, msg):
    print(f"{msg.topic} {msg.payload}")
    if bin("on") in msg.payload:
        GPIO.output(4, GPIO.HIGH)
    elif bin("off") in msg.payload:
        GPIO.output(4, GPIO.LOW)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

#创建链接
#borker, TCP Port, Websocket Port
client.connect("broker.emqx.io", 1883, 60)

#set GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(4, GPIO.OUT)

#设置网络循环堵塞，在调用disconnect()或者程序崩溃前，不会主动结束程序
client.loop_forever()