import time
import logging
import paho.mqtt.client as mqtt
import random
import argparse

class MqttErrors(object):
    def __init__(self):
        self.error_list = [
            'MQTT_ERR_AGAIN',
            'MQTT_ERR_SUCCESS',
            'MQTT_ERR_NOMEM',
            'MQTT_ERR_PROTOCOL',
            'MQTT_ERR_INVAL',
            'MQTT_ERR_NO_CONN',
            'MQTT_ERR_CONN_REFUSED',
            'MQTT_ERR_NOT_FOUND',
            'MQTT_ERR_CONN_LOST',
            'MQTT_ERR_TLS',
            'MQTT_ERR_PAYLOAD_SIZE',
            'MQTT_ERR_NOT_SUPPORTED',
            'MQTT_ERR_AUTH',
            'MQTT_ERR_ACL_DENIED',
            'MQTT_ERR_UNKNOWN',
            'MQTT_ERR_ERRNO',
            'MQTT_ERR_QUEUE_SIZE'
        ]

        self.error_map = {}

        for error_description in self.error_list:
            self.error_map[getattr(mqtt, error_description)] = error_description

    def get(self, error_value):
        return self.error_map.get(error_value)

class MqttClient(object):
    def __init__(self, server_address):

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(funcName)s.%(lineno)d - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        self.logger.addHandler(ch)

        self.logger.info("Initializing " + __name__)

        self.server_address = server_address
        self.topic = 'events'
        self._is_connected = False
        self.client = mqtt.Client()
        self.error_description = MqttErrors()

        # callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

        # start
        self.connect()


    def connect(self):
        self.logger.debug("Connecting to " + self.server_address)
        client_conn = self.client.connect_async(self.server_address, keepalive=5)
        if client_conn:
            self.logger.error("Couldn't connect")
            exit(1)
        self.logger.info("Connected")
        self.client.loop_start()


    def publish(self, event):
        while not self._is_connected:
            self.logger.info("Waiting connection.")
            time.sleep(1)
        try:
            mqtt_msg_info = self.client.publish(self.topic, event)
            self.client.loop(timeout=3)
            return_code, msg_id = mqtt_msg_info
            #self.logger.debug("Message ID {}. Return code {}.".format(msg_id, return_code))
            if return_code == mqtt.MQTT_ERR_NO_CONN:
                self.logger.error("Client not connected.")
            if not mqtt_msg_info.is_published():
                self.logger.error("Error publishing message. Return code {}: {}".format(return_code, self.error_description.get(return_code)))

        except Exception as ex:
            self.logger.error(ex)

    def on_connect(self, client, userdata, flags, rc):
        self.logger.info("Connected with result code {}: {}".format(rc, self.error_description.get(rc)))
        self._is_connected = True

    def on_disconnect(self, client, userdata, rc):
        self.logger.warn("Connection lost. Result code {}: {}".format(rc, self.error_description.get(rc)))
        self._is_connected = False

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

parser = argparse.ArgumentParser(description='Generate events and publish them to mqtt topic.')
parser.add_argument('ip', metavar='N', type=str, help='IP Address')
parser.add_argument('--n_events', metavar='N', type=str,  help='How many events will be generated')

args = parser.parse_args()
ip = args.ip
n_events = args.n_events

client = MqttClient(ip)

if not n_events:
    print("Publishing infinite events.")
    while True:
        n = random.randint(0, len(messages_universe)-1)
        try:
            client.publish(messages_universe[n])
        except Exception as ex:
            print "ERROR"
            print type(ex)
else:
    n_events = int(n_events)
    print("Publishing {} events.".format(n_events))

    for _ in range(n_events):
        n = random.randint(0, len(messages_universe)-1)
        try:
            client.publish(messages_universe[n])
        except Exception as ex:
            print "ERROR"
            print type(ex)

