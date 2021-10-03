from flask import Flask, render_template, request
import RPi.GPIO as GPIO
import board
import adafruit_dht
import time
import sqlite3
import paho.mqtt.client as mqtt

db_file = 'IoTMilestone1DB.db'
app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# set ports for LEDs
GPIO.setup(4, GPIO.OUT)  # set #4 as ouput port
GPIO.output(4, GPIO.LOW)  # initially turned off

# set ports for distance sensor
TRIG = 23
ECHO = 24
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)




def on_connect_led(client, userdata, flags, rc):
    print(f"client:{client} Connected with result code {rc}")
    client.subscribe("topic/led")

def on_message_led(client, userdata, message):
    msg=str(message.payload.decode("utf-8"))
    print(msg)
    if msg=="on":
        GPIO.output(4, GPIO.HIGH)
    elif msg=="off":
        GPIO.output(4, GPIO.LOW)


#set client for leds
ledc = mqtt.Client()
ledc.on_connect = on_connect_led
ledc.on_message = on_message_led
ledc.connect("broker.hivemq.com", 1883, 60)
ledc.loop_start()





"""
routes
"""

@app.route('/led/<action>')
def ledAction(action):
    #use MQTT to pulish message
    ledc.publish("topic/led", action)
    print("sent")
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


@app.route("/dht11")
def dht():
    dhtDevice = adafruit_dht.DHT11(board.D12, use_pulseio=False)
    msg = "failed to read the sensor, showing the newest record from the database"
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
            conn = sqlite3.connect(db_file)
            cur = conn.cursor()
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
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

        templateData = {
            'temperature': temperature,
            'humidity': humidity,
            'msg': msg
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
        templateData = {
            'temperature': temperature,
            'humidity': humidity,
            'msg': msg
        }
        conn.close()
    return render_template('dht11.html', **templateData)


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


@app.route("/led")
def led():
    ledState = GPIO.input(4)
    templateData = {
        'led': ledState,
    }
    return render_template('index.html', **templateData)





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
    templateData = {
        'dist': distance,
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



