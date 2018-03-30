# -*- coding: utf-8 -*-

import time
import logging
import paho.mqtt.client as mqtt
import random
import argparse
import threading

def configure_logger(logger):
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(threadName)s.%(name)s.%(funcName)s.%(lineno)d - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)


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

        self.logger = logging.getLogger(self.__class__.__name__)
        configure_logger(self.logger)

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
        client_conn = self.client.connect(self.server_address, keepalive=5)
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
            return_code, msg_id = mqtt_msg_info
            mqtt_msg_info.wait_for_publish()
            #self.logger.debug("Message ID {}. Return code {}.".format(msg_id, return_code))
            if return_code:
                self.logger.error("Error publishing message. Return code {}: {}".format(return_code, self.error_description.get(return_code)))

        except Exception as ex:
            self.logger.error(ex)

    def on_connect(self, client, userdata, flags, rc):
        self.logger.info("Connected with result code {}: {}".format(rc, self.error_description.get(rc)))
        self._is_connected = True

    def on_disconnect(self, client, userdata, rc):
        self.logger.warn("Connection lost. Result code {}: {}".format(rc, self.error_description.get(rc)))
        self._is_connected = False


class MqttPublisher(object):
    def __init__(self, server_address):

        self.logger = logging.getLogger(self.__class__.__name__)
        configure_logger(self.logger)

        self.server_address = server_address
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

        self.messages_universe = list()
        for k, v in messages.iteritems():
            for _ in range(v):
                self.messages_universe.append(k)

        random.shuffle(self.messages_universe)
        self.len_messages_universe = len(self.messages_universe)

        self.logger.info("Building Mqtt client")
        self.client = MqttClient(self.server_address)

    def publish_random_event(self):
        n = random.randint(0, self.len_messages_universe - 1)
        try:
            self.client.publish(self.messages_universe[n])
        except Exception as ex:
            print ex.message

    def publish(self, n_events):
        if n_events == 0:
            self.logger.info("Publishing events.")
            while True:
                self.publish_random_event()
        else:
            self.logger.info("Publishing {} events.".format(n_events))
            for e in range(n_events):
                self.publish_random_event()


class MqttPublisherThreading(object):
    def __init__(self, server_address, n_threads, n_events):
        self.logger = logging.getLogger(self.__class__.__name__)
        configure_logger(self.logger)

        self.server_address = server_address
        self.n_threads = int(n_threads)
        self.n_events = n_events
        self.logger.info("Threads {}. Events {}.".format(n_threads, n_events))

    def publish(self):
        def build_worker(n_events):
            obj = MqttPublisher(self.server_address)
            self.logger.info("Building worker")
            obj.publish(n_events)

        for t in range(self.n_threads):
            self.logger.info("Spawning thread {}/{}".format(t+1, n_threads))
            t = threading.Thread(target=build_worker, args=(self.n_events,))
            t.daemon = True
            t.start()

        while True:
            time.sleep(1)


parser = argparse.ArgumentParser(description='Generate events and publish them to mqtt topic.')
parser.add_argument('server_address', metavar='N', type=str, help='IP Address')
parser.add_argument('--n_events', metavar='N', type=str,  help='How many events will be generated')
parser.add_argument('--n_threads', metavar='N', type=str,  help='How many threads will be used')

args = parser.parse_args()
server_address = args.server_address
n_events = 0 if args.n_events is None else int(args.n_events)
n_threads = 1 if args.n_threads is None else int(args.n_threads)

mqtt_publisher = MqttPublisherThreading(server_address, n_threads, n_events)
mqtt_publisher.publish()

