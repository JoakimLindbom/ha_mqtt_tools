"""
Detect and reconfigure MQTT entities going offline

@author: 'Joakim Lindbom'
"""

import time

from entities import Entities

# TODO: Check if running under AppDaemon and create conditional imports
from hamqtt_paho import HaMqttPaho as HaMqtt
# from hamqtt_ad import HaMqttAD as HaMqtt


class TestMqtt:
    def __init__(self):
        self.BaseTopic = 'zigbee2mqtt/'

        self.topic = self.BaseTopic
        self.availability_counter = 0

        self.entities = Entities()
        self.mqtt = HaMqtt()
        self.mqtt.init("paho", self.BaseTopic, "mqtt")

    def init(self):
        self.mqtt.connect()
        self.mqtt.on_connect(self.on_connect)
        self.mqtt.on_message(self.on_message)

        self.mqtt.getBridgeDevices()

        try:
            self.mqtt.loop_forever()
        except KeyboardInterrupt:
            pass

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

    def log(self, msg):
        print(f"LOG> {msg}")

    def on_message(self, client, userdata, event, properties=None):
        payload = event.payload.decode('UTF-8')
        # self.log("topic: " + event.topic + " event:" + str(message.payload))
        self.log("topic: " + event.topic)
        if event.topic == self.BaseTopic + "bridge/devices":
            self.entities.unpack_bridge_devices(event.payload)
            self.subscribe_entity_statuses()
        elif event.topic.split("/")[2] == "availability":
            self.entities.getDeviceAvailability(event.topic.split("/")[1], payload)
            self.availability_counter += 1
            # self.log(f'{payload=}')
        else:
            self.log(f"Unhandled topic {event.topic}")

        if self.availability_counter > 55:  # TODO: Replace with separate thread + delay
            time.sleep(2)
            self.reconfigure_offline()

    def subscribe_entity_statuses(self):
        for e in self.entities:
            self.mqtt.subscribeDeviceAvailability(e)

    def reconfigure_offline(self):
        self.log(f"reconfigure_offline")

        for e in self.entities.get_offline_to_reconfigure():
            self.log(f"Reconfiguring {e}")
            self.mqtt.reconfigure(e)



if __name__ == "__main__":
    client = TestMqtt()
    client.init()
