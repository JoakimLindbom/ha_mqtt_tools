import paho.mqtt.client as mqtt
import json
import random


class HaMqtt:
    """
    Wrapping the AppDaemon API and paho API to make it runnable in two environments
    """
    environment_options = ["AppDaemon", "paho"]
    def __init__(self):
        self._environment = None

        self.mqtt_username = None
        self.mqtt_password = None
        self.broker = None
        self.port = None
        self.port_websocket = None
        self.port_ssl = None
        self.port_websocket_ssl = None
        self.client_id = None
        self.dont_reconfigure = None

        self.BaseTopic = None
        self.namespace = None

        self._mqtt = None

    def init(self, environment, base_topic, namespace):
        pass  # Abstract

    def connect(self):
        pass

    def on_connect(self, func):
        pass

    def on_message(self, func):
        pass

    def subscribe(self, topic):
        pass

    def unsubscribe(self, topic):
        pass

    def publish(self, topic, data):
        pass

    def listen_to_device(self, entityID):
        self.subscribe(self.BaseTopic + entityID)

    def subscribeDeviceAvailability(self, entityId):
        topic = self.BaseTopic + entityId + '/availability'
        # Remove any earlier subscription. It does not terminate if the app dies and AppDaemon continues running
        try:
            self.unsubscribe(topic)
        except:
            pass

        self.subscribe(topic)

    def reconfigure(self, entity):
        topic = self.BaseTopic + "bridge/request/device/configure"
        response_topic = self.BaseTopic + "bridge/response/"

        # status = ok or = error
        data = '{"id": "' + entity + '"}'
        self.log(f'MQTT reconfigure: {data}')
        self.publish(topic, data)

    @property
    def environment(self):
        return self._environment

    def getBridgeDevices(self):
        topic = self.BaseTopic + 'bridge/devices'
        #        self.log(f'Subscribing to : {topic}')

        # Remove any earlier subscription. It does not terminate if the app dies and AppDaemon continues running
        try:
            self.unsubscribe(topic)
        except:
            pass

        self.subscribe(topic)

    def loop_forever(self):
        pass

# Utilities
    def log(self, msg):
        print(f"LOG> {msg}")

    # TODO: Leave out for AppDaemon
