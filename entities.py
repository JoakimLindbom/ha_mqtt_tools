import json

class Entities:
    """
    Handles list of entities from MQTT
    Can be used to track online/offline entities and which to initiate reconfiguring
    """
    def __init__(self):
        self.entities = {}

        with open("secrets.json", encoding='utf8') as f:
            s = json.load(f)
            self.dont_reconfigure = s["dont_reconfigure"]

    def __iter__(self):
        yield from self.entities

    def __len__(self):
        return len(self.entities)

    def add(self, entity, device_type=None):
        e = {"entity": entity,
             "status": None,
             "reconfigure": True,
             "type": device_type
             }
        self.entities[entity] = e

    def get(self, entity):
        try:
            x = self.entities[entity]
            return x
        except KeyError:
            raise KeyError

    def set_status(self, entity, status, reconfigure=None):
        try:
            self.entities[entity]["status"] = status.lower()
            if reconfigure is not None:
                self.entities[entity]["reconfigure"] = reconfigure
        except KeyError:
            raise KeyError

    def set_dont_reconfigure(self, entities):
        try:
            if isinstance(entities, list):
                for e in entities:
                    self.entities[e]["reconfigure"] = False
            else:
                self.entities[entities]["reconfigure"] = False
        except KeyError:
            raise KeyError

# Utilities
    def log(self, msg):
        print(f"LOG> {msg}")

# Filters
    def is_offline(self, entity):
        x = self.get(entity)
        return x["status"] == 'offline'

    def get_offline(self, in_list=None):
        if in_list is None:
            return list(filter(lambda x: (self.get(x)["status"] == 'offline'), list(self.entities.keys())))
        else:
            return list(filter(lambda x: (self.get(x)["status"] == 'offline'), in_list))

    def is_reconfigure(self, entity):
        x = self.get(entity)
        return x["reconfigure"]

    def get_reconfigurables(self, in_list=None):
        if in_list is None:
            return list(filter(lambda x: (self.get(x)["reconfigure"]), list(self.entities.keys())))
        else:
            return list(filter(lambda x: (self.get(x)["reconfigure"]), in_list))

    def get_offline_to_reconfigure(self):
        return list(filter(lambda x: (self.is_offline(x)), list(filter(lambda x: (self.is_reconfigure(x)), self.entities))))

# MQTT Bridge handling
    def unpack_bridge_devices(self, message):
        b = json.loads(message)
        for c in b:
            if c["type"] != "Coordinator":
                self.add(c["friendly_name"])

        self.set_dont_reconfigure(self.dont_reconfigure)

    def getDeviceAvailability(self, entityId, message):  #FixMe: Rename to setDev...
        # status = message.decode('UTF-8')
        self.set_status(entityId, message.lower())
        if message.lower() == "offline":
            self.log(f"OFFLINE: {entityId}")
            # TODO: Start reconfig after x seconds
