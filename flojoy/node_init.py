from typing import Callable
from .dao import Dao


class NoInitFunctionError(Exception):
    pass


# contains value returned by a node's init function
class NodeInitContainer:
    def __init__(self, value=None):
        self.value = value

    def set(self, value):
        self.value = value

    def get(self):
        return self.value


class NodeInit:
    def __init__(self, func):
        self.func = func

    def __call__(self, node_id: str):
        return self.run(node_id)

    def run(self, node_id: str):
        daemon_container = NodeInitService().create_init_store(node_id)
        res = self.func()
        if res is not None:
            daemon_container.set(res)


# Wrapper for node_init functions, maps the node to the function that will initialize it.
def node_initialization(for_node):
    def decorator(func):
        func_init = NodeInit(func)
        NodeInitService().map_node_to_init_function(for_node, func_init)
        return func_init

    return decorator


class NodeInitService:
    """
    Class that handles different tasks related to node initialization
    """

    # this method will create the storage used for the node to hold whatever it initialized.
    def create_init_store(self, node_id):
        if self.has_init_store(node_id):
            raise ValueError("Storage for %s init object already exists!" % node_id)

        Dao.get_instance().set_init_container(node_id, NodeInitContainer())
        return self.get_init_store(node_id)

    # this method will get the storage used for the node to hold whatever it initialized.
    def get_init_store(self, node_id) -> NodeInitContainer:
        store = Dao.get_instance().get_init_container(node_id)
        if store is None:
            raise ValueError(
                "Storage for %s init object has not been initialized!" % node_id
            )
        return store

    # this method will check if a node has an init store already created.
    def has_init_store(self, node_id) -> bool:
        return Dao.get_instance().has_init_container(node_id)

    # this method will map a node to a function that will initialize it.
    def map_node_to_init_function(self, node_func, node_init_func):
        if NodeInitService().has_init_store(node_func.__name__):
            raise ValueError("Node %s already has an init store!" % node_func.__name__)
        Dao.get_instance().set_init_function(node_func, node_init_func)

    # this method will get the function that will initialize a node.
    def get_node_init_function(self, node_func) -> NodeInit:
        res = Dao.get_instance().get_init_function(node_func)
        if res is None:
            raise NoInitFunctionError(
                "Node %s does not have an init function!" % node_func.__name__
            )
        return res


def get_node_init_function(node_func: Callable) -> NodeInit:
    """
    Returns the function corresponding to the init function of the specified node.
    """
    return NodeInitService().get_node_init_function(node_func)
