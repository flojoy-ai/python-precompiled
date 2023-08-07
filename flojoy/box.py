class Box:
    def __init__(self, *args, **kwargs):
        self.__dict__.update(*args, **kwargs)
        for key, value in self.__dict__.items():
            self.__dict__[key] = self._to_box(value)

    def _to_box(self, value):
        if isinstance(value, dict):
            return Box(value)
        elif isinstance(value, list):
            return [self._to_box(x) for x in value]
        else:
            return value

    def __getattr__(self, item):
        return self.__dict__.get(item, None)

    def __setattr__(self, key, value):
        self.__dict__[key] = self._to_box(value)

    def __setitem__(self, key, value):
        self.__dict__[key] = self._to_box(value)

    def __getitem__(self, item, ignore_default=False):
        return self.__dict__.get(item, None) if ignore_default else self.__dict__[item]

    def __repr__(self):
        return str(self.__dict__)

    def to_dict(self):
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Box):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [v.to_dict() if isinstance(v, Box) else v for v in value]
            else:
                result[key] = value
        return result

    def get(self, key, default=None):
        return self.__dict__.get(key, default)
    
    def values(self):
        return self.__dict__.values()