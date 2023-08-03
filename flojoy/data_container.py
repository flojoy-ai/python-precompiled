import difflib
from ulab import numpy as np
from .box import Box
from typing import Union, Any, cast


def find_closest_match(given_str: str, available_str: list):
    closest_match = difflib.get_close_matches(given_str, available_str, n=1)
    if closest_match:
        return closest_match[0]
    else:
        return None


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

DCNpArrayType = np.ndarray[Union[int, float], np.dtype[Any]]
DCKwargsValue = Union[
    list,
    int,
    float,
    dict,
    DCNpArrayType,
    bytes,
    str,
    None,
]
ExtraType = Union[dict, None]


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
        "t": [*(value for value in allowed_keys if value not in ["t"])],
        "r": ["g", "b", "t", "a", "extra"],
        "g": ["r", "b", "t", "a", "extra"],
        "b": ["r", "g", "t", "a", "extra"],
        "a": ["r", "g", "b", "t", "extra"],
        "bytes": ["extra"],
        "text_blob": ["extra"],
        "extra": [*(k for k in allowed_keys if k not in ["extra"])],
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
        copied_instance = DataContainer(**self)
        return copied_instance

    def _ndarrayify(self, value: DCKwargsValue) -> Union[DCNpArrayType, dict]:
        if isinstance(value, int) or isinstance(value, float):
            return np.array([value])
        elif isinstance(value, dict):
            arrayified_value = {}
            for k, v in value.items():
                arrayified_value[k] = cast(DCNpArrayType, self._ndarrayify(v))
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
            raise ValueError("DataContainer keys must be any of ", DCKwargsValue)

    def __init__(  # type:ignore
        self, type="ordered_pair", **kwargs: DCKwargsValue
    ):
        self.type = type
        for k, v in kwargs.items():
            self[k] = v

    def __getattribute__(self, __name: str) -> Any:
        return super().__getattribute__(__name)

    def __getitem__(self, key: str, _ignore_default: bool = False) -> Any:
        return super().__getitem__(key, _ignore_default)  # type:ignore

    def __setitem__(self, key: str, value: DCKwargsValue) -> None:
        if (
            key not in ["type", "extra"]
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

    def __validate_key_for_type(self, data_type, key: str):
        if data_type.startswith("parametric_") and key != "t":
            splitted_type = data_type.split("parametric_")[1]
            self.__validate_key_for_type(splitted_type, key)
        else:
            if (
                key not in self.type_keys_map[data_type] + ["extra"]
                and data_type != "plotly"
            ):
                raise KeyError(
                    self.__build_error_text(
                        key, data_type, self.type_keys_map[data_type]
                    )
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

    def validate(self):
        dc_type = self.type
        if dc_type not in self.allowed_types:
            closest_type = find_closest_match(dc_type, self.allowed_types)
            helper_text = (
                'Did you mean: "%s" ?' % closest_type
                if closest_type
                else 'allowed types: "%s"' % ({", ".join(self.allowed_types)})
            )
            raise ValueError(
                'unsupported type "%s" passed to ' % dc_type
                + "DataContainer class, %s" % helper_text
            )
        dc_keys = list(self.keys())
        for k in dc_keys:
            if k != "type":
                self.__check_combination(
                    k,
                    list(key for key in dc_keys if key not in ["type", k]),
                    self.combinations[k],
                )
                self.__validate_key_for_type(dc_type, k)
        self.__check_for_missing_keys(dc_type, dc_keys)


class OrderedPair(DataContainer):
    def __init__(  # type:ignore
        self, x: DCNpArrayType, y: DCNpArrayType, extra: ExtraType = None
    ):
        super().__init__(type="ordered_pair", x=x, y=y, extra=extra)


class ParametricOrderedPair(DataContainer):
    def __init__(  # type:ignore
        self,
        x: DCNpArrayType,
        y: DCNpArrayType,
        t: DCNpArrayType,
        extra: ExtraType = None,
    ):
        super().__init__(type="parametric_ordered_pair", x=x, y=y, t=t, extra=extra)


class OrderedTriple(DataContainer):
    def __init__(  # type:ignore
        self,
        x: DCNpArrayType,
        y: DCNpArrayType,
        z: DCNpArrayType,
        extra: ExtraType = None,
    ):
        super().__init__(type="ordered_triple", x=x, y=y, z=z, extra=extra)


class ParametricOrderedTriple(DataContainer):
    def __init__(  # type:ignore
        self,
        x: DCNpArrayType,
        y: DCNpArrayType,
        z: DCNpArrayType,
        t: DCNpArrayType,
        extra: ExtraType = None,
    ):
        super().__init__(
            type="parametric_ordered_triple", x=x, y=y, z=z, t=t, extra=extra
        )


class Surface(DataContainer):
    def __init__(  # type:ignore
        self,
        x: DCNpArrayType,
        y: DCNpArrayType,
        z: DCNpArrayType,
        extra: ExtraType = None,
    ):
        super().__init__(type="surface", x=x, y=y, z=z, extra=extra)

    def validate(self):
        if self.z.ndim < 2:
            raise ValueError("z key must be of 2D array for Surface type!")
        super().validate()


class ParametricSurface(DataContainer):
    def __init__(  # type:ignore
        self,
        x: DCNpArrayType,
        y: DCNpArrayType,
        z: DCNpArrayType,
        t: DCNpArrayType,
        extra: ExtraType = None,
    ):
        super().__init__(type="parametric_surface", x=x, y=y, z=z, t=t, extra=extra)

    def validate(self):
        if self.z.ndim < 2:
            raise ValueError("z key must be of 2D array for Surface type!")
        super().validate()


class Scalar(DataContainer):
    def __init__(self, c: int | float, extra: ExtraType = None):  # type:ignore
        super().__init__(type="scalar", c=c, extra=extra)


class ParametricScalar(DataContainer):
    def __init__(self, c, t: DCNpArrayType, extra: ExtraType = None):  # type: ignore
        super().__init__(type="parametric_scalar", c=c, t=t, extra=extra)


class Vector(DataContainer):
    def __init__(self, v: DCNpArrayType, extra: ExtraType = None):  # type:ignore
        super().__init__(type="vector", v=v, extra=extra)


class ParametricVector(DataContainer):
    def __init__(  # type: ignore
        self, v: DCNpArrayType, t: DCNpArrayType, extra: ExtraType = None
    ):
        super().__init__(type="parametric_vector", v=v, t=t, extra=extra)


class Matrix(DataContainer):
    def __init__(self, m: DCNpArrayType, extra: ExtraType = None):  # type:ignore
        super().__init__(type="matrix", m=m, extra=extra)


class ParametricMatrix(DataContainer):
    def __init__(  # type: ignore
        self, m: DCNpArrayType, t: DCNpArrayType, extra: ExtraType = None
    ):
        super().__init__(type="parametric_matrix", m=m, t=t, extra=extra)


class Image(DataContainer):
    def __init__(  # type:ignore
        self,
        r: DCNpArrayType,
        g: DCNpArrayType,
        b: DCNpArrayType,
        a: DCNpArrayType | None = None,
        extra: ExtraType = None,
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
        r: DCNpArrayType,
        g: DCNpArrayType,
        b: DCNpArrayType,
        a: DCNpArrayType,
        t: DCNpArrayType,
        extra: ExtraType = None,
    ):
        super().__init__(type="parametric_image", r=r, g=g, b=b, a=a, t=t, extra=extra)


class Grayscale(DataContainer):
    def __init__(self, img: DCNpArrayType, extra: ExtraType = None):  # type:ignore
        super().__init__(type="grayscale", m=img, extra=extra)


class ParametricGrayscale(DataContainer):
    def __init__(  # type:ignore
        self, img: DCNpArrayType, t: DCNpArrayType, extra: ExtraType = None
    ):
        super().__init__(type="parametric_grayscale", m=img, t=t, extra=extra)
``