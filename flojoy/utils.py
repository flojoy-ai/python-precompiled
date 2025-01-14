from typing import Any, Callable
from .dao import Dao
from .config import FlojoyConfig
from .node_init import NodeInit, NodeInitService


__all__ = [
    "clear_flojoy_memory",
]

def set_offline():
    """
    Sets the is_offline flag to True, which means that results will not be sent to the backend via HTTP.
    Mainly used for precompilation
    """
    FlojoyConfig.get_instance().is_offline = True


def set_online():
    """
    Sets the is_offline flag to False, which means that results will be sent to the backend via HTTP.
    """
    FlojoyConfig.get_instance().is_offline = False


def set_debug_on():
    """
    Sets the print_on flag to True, which means that the print statements will be executed.
    """
    FlojoyConfig.get_instance().to_print = True

def set_debug_off():
    """
    Sets the print_on flag to False, which means that the print statements will not be executed.
    """
    FlojoyConfig.get_instance().to_print = False

def clear_flojoy_memory():
    Dao.get_instance().clear_job_results()
    Dao.get_instance().clear_small_memory()
    Dao.get_instance().clear_node_init_containers()

class NotEncodable(Exception):
    pass


def dump_str(result: Any, limit = None):
    result_str = str(result)
    return (
        result_str
        if limit is None or len(result_str) <= limit
        else result_str[:limit] + "..."
    )

def get_node_init_function(node_func: Callable) -> NodeInit:
    return NodeInitService().get_node_init_function(node_func)
