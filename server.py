from flask import Flask, render_template, request
import time
import sqlite3
from flask_mqtt import Mqtt
import json
import socket
import sys

db_file = 'IoTMilestone1DB.db'

hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = "mosquitto"
app.config['TEMPLATES_AUTO_RELOAD'] = False
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_TLS_ENABLED'] = False
app.config['MQTT_CLEAN_SESSION'] = True
mqtt = Mqtt(app)

mqtt.subscribe('queen/dht11_error')
mqtt.subscribe('queen/dht11_store')
mqtt.subscribe('queen/distance_store')
mqtt.subscribe('queen/led/action')
mqtt.subscribe('queen/led/state')


@mqtt.on_disconnect()
def handle_disconnect(client, userdata, rc):
    mqtt = Mqtt(app)
    mqtt.subscribe('queen/dht11_error')
    mqtt.subscribe('queen/dht11_store')
    mqtt.subscribe('queen/distance_store')
    mqtt.subscribe('queen/led/action')
    mqtt.subscribe('queen/led/state')

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print("client on server connected",flush=True,file=sys.stderr)


@mqtt.on_topic("queen/dht11_store") #read temp and humidity succeed, store the data to database
def store_dht_data(client, userdata, message):

    msg_r=str(message.payload.decode("utf-8"))
    msg_r=json.loads(msg_r)
    #store the data
    temperature=msg_r['temperature']
    humidity=msg_r['humidity']
    msg=msg_r['msg']
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    sql = 'insert into history_temperature_humidity(temperature, humidity, create_time) values(?,?,?)'
    data = (temperature, humidity, timestamp)
    cur.execute(sql, data)
    conn.commit()
    conn.close()
    mqtt.publish("queen/dht11", json.dumps(msg_r), retain=True)  # publish to clients on front end as well to show the data

@mqtt.on_topic("queen/dht11_error") #read temp and humidity failed,
def store_dht_data(client, userdata, message):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    newestData = cur.execute("select * from history_temperature_humidity order by id desc limit 1")
    for data in newestData:
        temperature = data[1]
        humidity = data[2]
    msg = "failed to read the sensor, showing the newest record from the database"
    templateData = {
        'temperature': temperature,
        'humidity': humidity,
        'msg': msg
    }

    mqtt.publish("queen/dht11", json.dumps(templateData),retain=True)

    conn.close()


@mqtt.on_topic("queen/distance_store")  # read temp and humidity succeed, store the data to database
def store_distance_data(client, userdata, message):
    msg_r=str(message.payload.decode("utf-8"))
    msg_r=json.loads(msg_r)
    print(msg_r,flush=True, file=sys.stderr)
    distance=msg_r['dist']
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    sql = 'insert into history_distance(distance, create_time) values(?,?)'
    data = (distance, timestamp)
    cur.execute(sql, data)
    conn.commit()
    conn.close()

    mqtt.publish("queen/distance", json.dumps(msg_r), retain=True)

@app.route("/")
def index():
    print("index", flush=True, file=sys.stderr)
    return render_template('index2.html')


@app.route('/led/<color>/<action>')
def ledAction(color,action):
    #use MQTT to pulish message
    message={
        'color': color,
        'action': action,
    }
    mqtt.publish("queen/led/action",json.dumps(message))

    return render_template('index2.html')

@app.route("/dht11")
def dht():
    message={
        'check': 'check',
    }
    mqtt.publish("queen/dht11_check", json.dumps(message))
    return render_template('dht11.html')

@app.route("/distance")
def dist():
    message={
        'check': 'check',
    }
    mqtt.publish("queen/distance_check",json.dumps(message))
    return render_template('distance.html')

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

@app.route("/ledStatus")
def ledStatusShow():
    mqtt.publish("check_led","check")
    return render_template('ledStatus.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=False)