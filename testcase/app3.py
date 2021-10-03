from flask import Flask, render_template, request
import RPi.GPIO as GPIO
import board
import adafruit_dht
import time
import sqlite3
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
import json


db_file = 'IoTMilestone1DB.db'


app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'
app.config['TEMPLATES_AUTO_RELOAD'] = False
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False
app.config['MQTT_CLEAN_SESSION'] = True
mqtt = Mqtt(app)
#socketio = SocketIO(app)
#bootstrap = Bootstrap(app)


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#set ports for LED
GPIO.setup(4, GPIO.OUT)  # set #4 as ouput port
GPIO.output(4, GPIO.LOW)  # initially turned off
#set ports for distance sensor
TRIG=23
ECHO=24
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

'''
Connect and handle messages
'''

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('start')
    mqtt.subscribe('actuator/led')
    mqtt.subscribe('sensor/dht11')
    print("connected")

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )

@mqtt.on_topic('actuator/led')
def led_mqtt_message(client, userdata, message):
    payload = message.payload.decode()
    print(payload)
    if payload == 'on':
        GPIO.output(4, GPIO.HIGH)
    else:
        GPIO.output(4, GPIO.LOW)

@mqtt.on_topic('sensor/dht11')
def temp_sensor_message(client, userdata, message):
    print("receive sensor")
    payload = message.payload.decode()
    print(payload)
'''
Routes:
'''
@app.route("/led")
def led():
    ledState = GPIO.input(4)
    templateData = {
        'led': ledState,
    }
    return render_template('index.html', **templateData)

@app.route("/")
def index():
    ledState = GPIO.input(4)
    templateData = {
        'led': ledState,
    }
    return render_template('index.html', **templateData)

@app.route('/led/blue/<action>')
def ledAction(action):
    if action=="on":
        mqtt.publish('actuator/led', 'on')
    else:
        mqtt.publish('actuator/led','off')

    ledState = GPIO.input(4)
    templateData = {
        'led': ledState,
    }
    mqtt.publish('led/state',ledState)
    return render_template('index.html', **templateData)

@app.route("/dht11")
def dht():

    dhtDevice = adafruit_dht.DHT11(board.D12,use_pulseio=False)
    msg = "failed to read the sensor, showing the newest record from the database"
    try:
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity
        if humidity is not None and temperature is not None:
            msg="read from the sensor successfully"
            templateData={
                'temperature':temperature,
                'humidity': humidity,
                'msg':msg
           }
            conn = sqlite3.connect(db_file)
            cur = conn.cursor()
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            sql = 'insert into history_temperature_humidity(temperature, humidity, create_time) values(?,?,?)'
            data = (temperature, humidity, timestamp)
            cur.execute(sql, data)
            conn.commit()
            conn.close()
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going

        dhtDevice.exit()
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        newestData = cur.execute("select * from history_temperature_humidity order by id desc limit 1")
        for data in newestData:
            temperature = data[1]
            humidity = data[2]

        templateData={
            'temperature': temperature,
            'humidity': humidity,
            'msg':msg
        }
        conn.close()
    except Exception as error:
        dhtDevice.exit()
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        newestData = cur.execute("select * from history_temperature_humidity order by id desc limit 1")
        for data in newestData:
            temperature = data[1]
            humidity = data[2]
        templateData={
            'temperature': temperature,
            'humidity': humidity,
            'msg': msg
        }
        conn.close()

    mqtt.publish('sensor/dht11',json.dumps(templateData))
    return render_template('dht11.html',**templateData)

@app.route("/tempHistoryData")
def histiryData():
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    history_data = cur.execute("select * from history_temperature_humidity order by id desc limit 30")
    history_data_list = []
    for data in history_data:
        history_data_list.append(data)
    conn.close()
    templateData = {
        'historyData': history_data_list
    }
    return render_template('tempHistoryData.html', **templateData)



@app.route("/distance")
def dist():
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
    templateData={
        'dist':distance,
    }
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    sql = 'insert into history_distance(distance, create_time) values(?,?)'
    data = (distance, timestamp)
    cur.execute(sql, data)
    conn.commit()
    conn.close()
    return render_template('distance.html', **templateData)

@app.route("/distHistoryData")
def distHist():
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    history_data = cur.execute("select * from history_distance order by id desc limit 30")
    history_data_list = []
    for data in history_data:
        history_data_list.append(data)
    conn.close()
    templateData = {
        'historyData': history_data_list
    }
    return render_template('distHistoryData.html', **templateData)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)


