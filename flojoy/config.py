class FlojoyConfig:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = FlojoyConfig()
        return cls._instance

    def __init__(self):
        self.is_offline = False
        self.to_print = False

# TODO make log levels? 
def logger(*to_print):
    if FlojoyConfig.get_instance().to_print:
        print(*to_print)
