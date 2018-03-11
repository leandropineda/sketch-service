import time
import logging
import paho.mqtt.client as mqtt
import random

class MqttClient(object):
    def __init__(self, server_address):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s.%(lineno)d - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        self.logger.addHandler(ch)

        self.logger.info("Initializing " + __name__)

        self.server_address = server_address
        self.topic = 'events'

        self.client = mqtt.Client()

        # callbacks
        self.client.on_connect = self.on_connect

        self.connect()



    def connect(self):
        self.logger.debug("Connecting to " + self.server_address)
        client_conn = self.client.connect(self.server_address, keepalive=5)
        if client_conn:
            self.logger.error("Couldn't connect")
            exit(1)
        self.logger.info("Connected")

    def publish(self, event):
        try:
            mqtt_msg_info = self.client.publish(self.topic, event)
            if not mqtt_msg_info.is_published():
                self.logger.error("Error publishing message")

        except Exception as ex:
            self.logger.error(ex)

    def on_connect(self, client, userdata, flags, rc):
        self.logger.info("Connected with result code " + str(rc))


messages = dict()
messages['Message1'] = 50
messages['Message2'] = 100
messages['Message3'] = 4
messages['Message4'] = 20
messages['Message5'] = 4
messages['Message6'] = 5
messages['Message7'] = 4
messages['Message8'] = 10
messages['Message9'] = 1
messages['Message10'] = 1

messages_universe = list()
for k, v in messages.iteritems():
    for _ in range(v):
        messages_universe.append(k)

random.shuffle(messages_universe)


n_events = 1000000
client = MqttClient('127.0.0.1')

for _ in range(n_events):
    n = random.randint(0, len(messages_universe)-1)
    try:
        client.publish(messages_universe[n])
    except Exception as ex:
        print "ERROR"
        print type(ex)

