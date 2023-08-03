class Box:
    def __init__(self, dictionary=None):
        if dictionary is None:
            dictionary = {}
        self._data = dictionary

    def __getattr__(self, key):
        if key in self._data:
            value = self._data[key]
            if isinstance(value, list):
                return BoxList(value)
            elif isinstance(value, dict):
                return Box(value)
            else:
                return value
        else:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        if key == '_data':
            super().__setattr__(key, value)
        else:
            self._data[key] = value

    def __repr__(self):
        return repr(self._data)

class BoxList(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, key):
        item = super().__getitem__(key)
        if isinstance(item, dict):
            return Box(item)
        elif isinstance(item, list):
            return BoxList(item)
        else:
            return item

