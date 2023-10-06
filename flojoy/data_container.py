import numpy as np
from .box import Box
from typing import Union, Any, cast

# DCType = Literal[
#     "grayscale",
#     "image",
#     "matrix",
#     "ordered_pair",
#     "ordered_triple",
#     "bytes",
#     "text_blob",
#     "scalar",
#     "surface",
#     "vector",
#     "parametric_grayscale",
#     "parametric_image",
#     "parametric_matrix",
#     "parametric_ordered_pair",
#     "parametric_ordered_triple",
#     "parametric_scalar",
#     "parametric_surface",
#     "parametric_vector",
# ]

class DCNpArrayType: 0

class DataContainer(Box):
    """
    A class that processes various types of data and supports dot assignment

    Learn more: https://github.com/flojoy-io/flojoy-python/issues/4

    Usage
    -----
    import numpy as np

    v = DataContainer()

    v.x = np.linspace(1,20,0.1)

    v.y = np.sin(v.x)

    v.type = 'ordered_pair'

    """

    # allowed_types = list(typing.get_args(DCType))
    allowed_keys = [
        "x",
        "y",
        "z",
        "t",
        "v",
        "m",
        "c",
        "r",
        "g",
        "b",
        "a",
        "text_blob",
        "fig",
        "extra",
    ]
    combinations = {
        "x": ["y", "t", "z", "extra"],
        "y": ["x", "t", "z", "extra"],
        "z": ["x", "y", "t", "extra"],
        "c": ["t", "extra"],
        "v": ["t", "extra"],
        "m": ["t", "extra"],
        "t": [value for value in allowed_keys if value not in ["t"]],
        "r": ["g", "b", "t", "a", "extra"],
        "g": ["r", "b", "t", "a", "extra"],
        "b": ["r", "g", "t", "a", "extra"],
        "a": ["r", "g", "b", "t", "extra"],
        "bytes": ["extra"],
        "text_blob": ["extra"],
        "extra": [k for k in allowed_keys if k not in ["extra"]],
        "fig": ["t", "extra"],
    }
    type_keys_map = {
        "matrix": ["m"],
        "vector": ["v"],
        "grayscale": ["m"],
        "image": ["r", "g", "b", "a"],
        "ordered_pair": ["x", "y"],
        "ordered_triple": ["x", "y", "z"],
        "surface": ["x", "y", "z"],
        "scalar": ["c"],
        "bytes": ["b"],
        "text_blob": ["text_blob"],
    }

    SKIP_ARRAYIEFY_TYPES = [
        str,
        bytes,
        np.ndarray,
    ]  # value types not to be arrayified

    def copy(self):
        # Create an instance of DataContainer class
        copied_instance = DataContainer()
        instance_dict = self.__dict__
        for k, v in instance_dict.items():
            setattr(copied_instance, k, v)
        return copied_instance

    def _ndarrayify(self, value):
        if isinstance(value, int) or isinstance(value, float):
            return np.array([value])
        elif isinstance(value, dict):
            arrayified_value = {}
            for k, v in value.items():
                arrayified_value[k] = self._ndarrayify(v)
            return arrayified_value
        # elif isinstance(value, box_list.BoxList):
        #     arrayified_value = {}
        #     for k, v in value.__dict__.items():
        #         arrayified_value[k] = cast(DCNpArrayType, self._ndarrayify(v))
        #     return arrayified_value
        elif isinstance(value, list):
            return np.array(value)
        elif value is None:
            return value
        else:
            raise ValueError("DataContainer keys are of wrong type")

    def __init__(  # type:ignore
        self, type="ordered_pair", **kwargs
    ):
        self.type = type
        for k, v in kwargs.items():
            self[k] = v

    def __getattribute__(self, __name: str) -> Any:
        return super().__getattribute__(__name)

    def __getitem__(self, key: str, _ignore_default: bool = False) -> Any:
        return super().__getitem__(key, _ignore_default)  # type:ignore

    def __setitem__(self, key: str, value) -> None:
        if (
            key not in ["type", "extra", "c"]
            and type(value) not in self.SKIP_ARRAYIEFY_TYPES
        ):
            formatted_value = self._ndarrayify(value)
            super().__setitem__(key, formatted_value)  # type:ignore
        else:
            super().__setitem__(key, value)  # type: ignore

    def __check_combination(self, key: str, keys: list, allowed_keys: list):
        for i in keys:
            if i not in allowed_keys:
                raise ValueError(
                    "You can't have '%s' and '%s' keys together for '%s' type!"
                    % (key, i, self.type)
                )

    def __check_for_missing_keys(self, dc_type, keys: list):
        if dc_type.startswith("parametric_"):
            if "t" not in keys:
                raise KeyError('t key must be provided for "%s"' % dc_type)
            t = self["t"]
            is_ascending_order = all(t[i] <= t[i + 1] for i in range(len(t) - 1))
            if is_ascending_order is not True:
                raise ValueError("t key must be in ascending order")
            splitted_type = dc_type.split("parametric_")[1]
            self.__check_for_missing_keys(splitted_type, keys)
        else:
            for k in self.type_keys_map[dc_type]:
                if k not in keys:
                    raise KeyError(
                        '"%s" key must be provided for type "%s"' % (k, dc_type)
                    )

    def __build_error_text(self, key: str, data_type: str, available_keys: list):
        return (
            'Invalid key "%s" provided for data type "%s", ' % (key, data_type)
            + 'supported keys: {", ".join(available_keys)}'
        )


class OrderedPair(DataContainer):
    def __init__(  # type:ignore
        self, x, y, extra = None
    ):
        super().__init__(type="ordered_pair", x=x, y=y, extra=extra)


class ParametricOrderedPair(DataContainer):
    def __init__(  # type:ignore
        self,
        x,
        y,
        t,
        extra = None,
    ):
        super().__init__(type="parametric_ordered_pair", x=x, y=y, t=t, extra=extra)


class OrderedTriple(DataContainer):
    def __init__(  # type:ignore
        self,
        x,
        y,
        z,
        extra = None,
    ):
        super().__init__(type="ordered_triple", x=x, y=y, z=z, extra=extra)


class ParametricOrderedTriple(DataContainer):
    def __init__(  # type:ignore
        self,
        x,
        y,
        z,
        t,
        extra= None,
    ):
        super().__init__(
            type="parametric_ordered_triple", x=x, y=y, z=z, t=t, extra=extra
        )


class Surface(DataContainer):
    def __init__(  # type:ignore
        self,
        x,
        y,
        z,
        extra = None,
    ):
        super().__init__(type="surface", x=x, y=y, z=z, extra=extra)


class ParametricSurface(DataContainer):
    def __init__(  # type:ignore
        self,
        x,
        y,
        z,
        t,
        extra = None,
    ):
        super().__init__(type="parametric_surface", x=x, y=y, z=z, t=t, extra=extra)


class Scalar(DataContainer):
    def __init__(self, c: int | float, extra = None):  # type:ignore
        super().__init__(type="scalar", c=c, extra=extra)


class ParametricScalar(DataContainer):
    def __init__(self, c, t, extra = None):  # type: ignore
        super().__init__(type="parametric_scalar", c=c, t=t, extra=extra)


class Vector(DataContainer):
    def __init__(self, v, extra = None):  # type:ignore
        super().__init__(type="vector", v=v, extra=extra)


class ParametricVector(DataContainer):
    def __init__(  # type: ignore
        self, v, t, extra = None
    ):
        super().__init__(type="parametric_vector", v=v, t=t, extra=extra)


class Matrix(DataContainer):
    def __init__(self, m, extra = None):  # type:ignore
        super().__init__(type="matrix", m=m, extra=extra)


class ParametricMatrix(DataContainer):
    def __init__(  # type: ignore
        self, m, t, extra = None
    ):
        super().__init__(type="parametric_matrix", m=m, t=t, extra=extra)


class Image(DataContainer):
    def __init__(  # type:ignore
        self,
        r,
        g,
        b,
        a = None,
        extra = None,
    ):
        super().__init__(type="image", r=r, g=g, b=b, a=a, extra=extra)


class Bytes(DataContainer):
    def __init__(
        self,
        b: bytes,
    ):
        super().__init__(type="bytes", b=b)


class TextBlob(DataContainer):
    def __init__(self, text_blob: str):
        super().__init__(type="text_blob", text_blob=text_blob)


class ParametricImage(DataContainer):
    def __init__(  # type:ignore
        self,
        r,
        g,
        b,
        a,
        t,
        extra = None,
    ):
        super().__init__(type="parametric_image", r=r, g=g, b=b, a=a, t=t, extra=extra)


class Grayscale(DataContainer):
    def __init__(self, img, extra = None):  # type:ignore
        super().__init__(type="grayscale", m=img, extra=extra)


class ParametricGrayscale(DataContainer):
    def __init__(  # type:ignore
        self, img, t, extra = None
    ):
        super().__init__(type="parametric_grayscale", m=img, t=t, extra=extra)
