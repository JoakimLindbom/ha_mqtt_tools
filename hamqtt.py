environment_options = ["AppDaemon", "paho"]


class HaMqtt:
    """
    Wrapping the AppDaemon API and paho API to make it runnable in two environments
    """

    def __init__(self):
        self._environment = None

    def init(self, environment):
        self._environment = environment if environment in environment_options else None
        if self._environment is None:
            raise ValueError

    @property
    def environment(self):
        return self._environment
