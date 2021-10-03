# IoTMilestone3_Pi
These codes should run on raspberry Pi locally
## Set up

### 1. Clone this repo
```shell
 $ git clone https://github.com/panyijing1997/iot2restructured.git
```
### 2. Build the docker image for the server
```shell
 $ cd iot2restructured
 $ docker build -t server .
 ```
### 3. Build the image for the clients app
```shell
$ cd clients
$ docker build -t clients .
```
### 4. run the images
```shell
$ cd ..
$ docker-compose up
```
Then visit `[your RPi's ip address]:8080` in broswer

## possible error
If you run into error of '<span style="color:red">Fatal Python error: init_interp_main: can’t initialize time ... ... PermissionError: [Errno 1] Operation not permitted</span>'. Please use the following commands:
(This seems to be a problem of the newest docker version and old version of library 'libseccomp2')
```shell
 $ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 04EE7237B7D453EC 648ACFD622F3D138
 $ echo "deb http://deb.debian.org/debian buster-backports main" | sudo tee -a /etc/apt/sources.list.d/buster-backports.list
 $ sudo apt update
 $ sudo apt install -t buster-backports libseccomp2
```



