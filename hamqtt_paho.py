import paho.mqtt.client as mqtt
import json
import random
from hamqtt import HaMqtt


class HaMqttPaho(HaMqtt):
    """
    Implementing a subclass for paho environments
    """

    def __init__(self):
        super().__init__()

    def init(self, environment, base_topic, namespace):
        self._environment = environment if environment in self.environment_options else None
        if self._environment is None:
            raise ValueError
        if self._environment == "paho":
            with open("secrets.json", encoding='utf8') as f:
                s = json.load(f)
                self.mqtt_username = s["mqtt"]["user"]
                self.mqtt_password = s["mqtt"]["password"]
                self.broker = s["mqtt"]["broker"]
                self.port = s["mqtt"]["port"]
                self.port_websocket = s["mqtt"]["port_websocket"]
                self.port_ssl = s["mqtt"]["port_ssl"]
                self.port_websocket_ssl = s["mqtt"]["port_ssl_websocket"]
                self.client_id = f'python-mqtt-{random.randint(0, 1000)}'
            self.namespace = namespace
            self.BaseTopic = base_topic
            self._mqtt = mqtt.Client()
            self._mqtt.username_pw_set(self.mqtt_username, self.mqtt_password)
        #super().init(environment, base_topic, namespace)

    def connect(self):
        self._mqtt.connect(self.broker, self.port)

    def on_connect(self, func):
        self._mqtt.on_connect = func

    def on_message(self, func):
        self._mqtt.on_message = func

    def subscribe(self, topic):
        self._mqtt.subscribe(topic, 2)

    def unsubscribe(self, topic):
        self._mqtt.unsubscribe(topic, 2)

    def publish(self, topic, data):
        self._mqtt.publish(topic, data)

    def loop_forever(self):
        self._mqtt.loop_forever()

