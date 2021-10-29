# IoTMilestone3 (Codes in RPi)
These codes should run on Pi locally.

**Note:** Our system doesn't distinguish different RPis, and webpages can show current sensor values for only one RPi at the same time, so we **will not** keep our RPi running when you test your RPi :) But the data from your RPi can still be written in our cloud database. 

**update on 13 Oct.**: at the start of every 10 seconds interval, the sensors will send measured data to broker and data will stored in the database. And these data will also show **lively** on the webpage . (If DHT11 failed, it will try again at the start of the next interval, you can see in the terminal window if it fails or successes. So sometimes the temperatue&humidity webpage does not update just because DHT11 fails several times in a row, you can just wait for the next interval or try click the "meausre again" button to manually check.)

You can see historical records for around every 10 seconds for both temperatue&humidity and distance data as the following examples:
![](./img/1.png)
![](./img/2.jpg)

While we still preseve the function of mannually choose to measure the data (including showing on the webpage and storing in historical records)

The link to the cloud components: http://milestone3v3.westeurope.azurecontainer.io [expired]

Codes for cloud components: https://github.com/panyijing1997/IoTMilestone3_cloud
## Set up

Connection of sensors and RPi:
https://github.com/panyijing1997/IoTCourseMilestone1

### 1. Clone this repo and go to the root
```shell
 $ git https://github.com/panyijing1997/IoTMilestone3_Pi.git
 $ cd IoTMilestone3_Pi
```
### 2. Build the docker image for broker
```shell
 $ cd mqtt
 $ docker build -t mqtt .
 $ cd ..
 ```
### 3. Build the image for the sensor clients
```shell
$ cd clients
$ docker build -t clients .
$ cd ..
```
### 4. build the image for the server and run all images together
```shell
$ docker-compose build
$ docker-compose up
```

**note:** Very very low probability that `docker-compose up` will run into a error with `server_1` image (It only happens only once to me), the solution is just run `docker-compose up` again.

Then visit `[your RPi's ip address]:8080` in broswer.


Use chrome or Edge if other broswers not work well.

## possible error
If you run into error of '<span style="color:red">Fatal Python error: init_interp_main: can’t initialize time ... ... PermissionError: [Errno 1] Operation not permitted</span>'. Please use the following commands:
(This seems to be a problem of the newest docker version and old version of library 'libseccomp2')
```shell
 $ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 04EE7237B7D453EC 648ACFD622F3D138
 $ echo "deb http://deb.debian.org/debian buster-backports main" | sudo tee -a /etc/apt/sources.list.d/buster-backports.list
 $ sudo apt update
 $ sudo apt install -t buster-backports libseccomp2
```




