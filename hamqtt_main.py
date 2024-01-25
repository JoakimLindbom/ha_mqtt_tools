"""
Detect and reconfigure MQTT entities going offline

@author: 'Joakim Lindbom'
"""

import json
import time
import paho.mqtt.client as mqtt
import random
from entities import Entities


class TestMqtt:
    def __init__(self):
        self.BaseTopic = 'zigbee2mqtt/'
        self.namespace = "mqtt"  # matches appdaemon.yaml

        with open("secrets.json") as f:
            s = json.load(f)
            self.mqtt_username = s["mqtt"]["user"]
            self.mqtt_password = s["mqtt"]["password"]
            self.broker = s["mqtt"]["broker"]
            self.port = s["mqtt"]["port"]
            self.port_websocket = s["mqtt"]["port_websocket"]
            self.port_ssl = s["mqtt"]["port_ssl"]
            self.port_websocket_ssl = s["mqtt"]["port_ssl_websocket"]
            self.client_id = f'python-mqtt-{random.randint(0, 1000)}'
            self.dont_reconfigure = s["dont_reconfigure"]  # FixMe: Check UTF-8 encoding?
        self._mqtt = mqtt.Client()
        self.topic = self.BaseTopic
        self.availability_counter = 0

        self.entities = Entities()

    def init(self):
        self._mqtt.username_pw_set(self.mqtt_username, self.mqtt_password)
        self._mqtt.on_connect = self.on_connect
        self._mqtt.on_message = self.on_message
        self._mqtt.connect(self.broker, self.port)

        self.getBridgeDevices()

        try:
            self._mqtt.loop_forever()
        except KeyboardInterrupt:
            pass

    def listen_to_device(self, entityID):
        self.topic = self.BaseTopic + entityID
        self._mqtt.subscribe(self.topic, 2)

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

    def log(self, msg):
        print(f"LOG> {msg}")

    def on_message(self, client, userdata, event, properties=None):
        payload = event.payload.decode('UTF-8')
        # self.log("topic: " + event.topic + " event:" + str(message.payload))
        self.log("topic: " + event.topic)
        if event.topic == self.BaseTopic + "bridge/devices":
            self.unpack_bridge_devices(event.payload)
            self.subscribe_entity_statuses()
            self.entities.set_dont_reconfigure(self.dont_reconfigure)
        elif event.topic.split("/")[2] == "availability":
            self.getDeviceAvailability(event.topic.split("/")[1], payload)
            self.availability_counter += 1
            # self.log(f'{payload=}')
        else:
            self.log(f"Unhandeld topic {event.topic}")

        if self.availability_counter > 62:
            time.sleep(2)
            self.reconfigure_offline()
        # self.log(f"{len(self.entities)=}")

    def unpack_bridge_devices(self, message):
        b = json.loads(message)
        for c in b:
            if c["type"] != "Coordinator":
                self.entities.add(c["friendly_name"])

    def subscribe_entity_statuses(self):
        for e in self.entities:
            self.subscribeDeviceAvailability(e)

    def subscribeDeviceAvailability(self, entityId):
        topic = self.BaseTopic + entityId + '/availability'
        # self.log(f'Subscribing to : {topic}')
        # Remove any earlier subscription. It does not terminate if the app dies and AppDaemon continues running
        try:
            self._mqtt.unsubscribe(topic)
        except:
            pass

        self._mqtt.subscribe(topic)
        # self._mqtt.listen_event(self.receiveDeviceAvailability, "MQTT_MESSAGE", topic=topic)

    def getDeviceAvailability(self, entityId, message):
        # status = message.decode('UTF-8')
        # self.log(f"{entityId=} - {status=}")
        self.entities.set_status(entityId, message.lower())
        if message.lower() == "offline":
            self.log(f"OFFLINE: {entityId}")
            # TODO: Start reconfig after x seconds

    def getBridgeDevices(self):
        topic = self.BaseTopic + 'bridge/devices'
        #        self.log(f'Subscribing to : {topic}')

        # Remove any earlier subscription. It does not terminate if the app dies and AppDaemon continues running
        try:
            self._mqtt.unsubscribe(topic)
        except:
            pass

        self._mqtt.subscribe(topic)

    def reconfigure_offline(self):
        self.log(f"reconfigure_offline")
        for e in list(filter(self.entities.is_reconfigure(
                 filter(self.entities.is_offline,
                        self.entities.entities)))):
            self.log(f"Reconfiguring {e}")
            self.reconfigure(e)

    def reconfigure(self, entity):
        topic = self.BaseTopic + "bridge/request/device/configure"
        response_topic = self.BaseTopic + "bridge/response/"

        # status = ok or = error
        data = '{"id": "' + entity + '"}'
        self.log(f'MQTT reconfigure: {data}')
        # self._mqtt.mqtt_publish(topic, data)
        self._mqtt.publish(topic, data)


if __name__ == "__main__":
    client = TestMqtt()
    client.init()
