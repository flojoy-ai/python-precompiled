from typing import Any, Union


class NodeReference:
    """Node parameter type"""

    def __init__(self, ref: str) -> None:
        self.ref = ref

    def unwrap(self):
        return self.ref


class Array:
    """Node parameter type of `list[str | float | int]`"""

    def __init__(self, ref: list) -> None:
        self.ref = ref

    def unwrap(self):
        return self.ref


def format_param_value(value: Any, value_type: str):
    if value_type == "Array":
        s = str(value)
        parsed_value = parse_array(s, [str, float, int], "list[int | float | str]")
        return Array(parsed_value)
    elif value_type == "float":
        return float(value)
    elif value_type == "int":
        return int(value)
    elif value_type == "bool":
        return bool(value)
    elif value_type == "NodeReference":
        return NodeReference(str(value))
    elif value_type == "list[str]":
        return parse_array(str(value), [str], "list[str]")
    elif value_type == "list[float]":
        return parse_array(str(value), [float], "list[float]")
    elif value_type == "list[int]":
        return parse_array(str(value), [int], "list[int]")
    elif value_type == "select" or value_type == "str":
        return str(value)
    else:
        return value



def parse_array(
    str_value: str, type_list: list, param_type: str
) -> list:
    if not str_value:
        return []

    val_list = [val.strip() for val in str_value.split(",")]
    # First try to cast into int, then float, then keep as string if all else fails
    for t in type_list:
        try:
            return list(map(t, val_list))
        except ValueError:
            continue
    
    val1 = ','.join([str(t) for t in type_list])
    val2 = ' | '.join([t.__name__ for t in type_list])

    raise ValueError(
        "Couldn't parse list items with type %s." % val1
        + "Value should be comma (',') separated %s for parameter type %s." % (val2, param_type)
    )
