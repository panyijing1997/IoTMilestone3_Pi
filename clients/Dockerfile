FROM arm32v7/python:3
WORKDIR /clients
RUN pip3 install --upgrade pip
RUN pip3 install adafruit-circuitpython-dht
RUN pip3 install paho-mqtt
RUN pip3 install --upgrade --pre rpi.gpio

COPY . .


EXPOSE 8081
CMD [ "python3","-u", "clients.py"]