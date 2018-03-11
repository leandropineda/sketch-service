# Sketch service: simple real-time anomalous event detection on events data streams

## Requirements
The system is shipped using docker-compose. You need to install:

* **Docker**: https://docs.docker.com/install/
* **Docker-compose**: https://docs.docker.com/compose/install/

## Run
To change any parameter, edit `config.yml`. Relevant sections are:

**sketchConfig**

* rows: number of rows on sketches

* cols: number of columns on sketches

* prime: prime number used for detection (must be a prime number)

**detectionParameters**

* heavyHitterThreshold: threshold for heavy hitter detection

* heavyChangerThreshold: threshold for heavy changer detection

* sketchRotationInterval: epoch duration

* maxHistoryQueueLength: how many epochs are kept on the service

Run the service by using:

	$ docker-compose up

## Test
A simple python script is provided. It will generate and submit messages to the service to test if everything works fine. Python class provided can be used to write your own client.

	$ cd client/
	$ python client.py

	