import numpy as np
from typing import Any, Callable

MAX_LIST_SIZE = 1000

"""
Used by clients to create a new instance of the datastorage
"""


def create_storage():
    return Dao.get_instance()


"""
This class is a Singleton that acts as a in-memory datastorage

IMPORTANT: The commented code should not be removed, as it acts as a reference for the future
in case we need to implement a Redis based datastorage
"""


class Dao:
    _instance = None

    @classmethod
    def get_instance(cls):
        if Dao._instance is None:
            Dao._instance = Dao()
        return Dao._instance

    def __init__(self):
        self.storage = {}  # small memory
        self.job_results = {}
        self.node_init_container = {}
        self.node_init_func = {}

    """
    METHODS FOR JOB RESULTS
    """

    def get_job_result(self, job_id: str) -> Any | None:
        res = self.job_results.get(job_id, None)
        if res is None:
            raise ValueError("Job result with id %s does not exist" % job_id)
        return res

    def post_job_result(self, job_id: str, result: Any):
        self.job_results[job_id] = result

    def clear_job_results(self):
        self.job_results.clear()

    def job_exists(self, job_id: str) -> bool:
        return job_id in self.job_results.keys()

    def delete_job(self, job_id: str):
        self.job_results.pop(job_id, None)

    """
    METHODS FOR SMALL MEMORY
    """

    def clear_small_memory(self):
        self.storage.clear()

    def check_if_valid(self, result: Any | None, expected_type: Any):
        if result is not None and not isinstance(result, expected_type):
            raise ValueError(
                "Expected %s type, but got %s instead!" % (expected_type, type(result))
            )

    def set_np_array(self, memo_key: str, value):
        self.storage[memo_key] = value

    def set_str(self, key: str, value: str):
        self.storage[key] = value

    def get_np_array(self, memo_key: str):
        encoded = self.storage.get(memo_key, None)
        self.check_if_valid(encoded, np.ndarray)
        return encoded

    def get_str(self, key: str):
        encoded = self.storage.get(key, None)
        return encoded

    def get_obj(self, key: str):
        r_obj = self.storage.get(key, None)
        self.check_if_valid(r_obj, dict)
        return r_obj

    def set_obj(self, key: str, value):
        self.storage[key] = value

    def delete_object(self, key: str):
        self.storage.pop(key)

    def remove_item_from_set(self, key: str, item: Any):
        res = self.storage.get(key, None)
        self.check_if_valid(res, set)
        if not res:
            return
        res.remove(item)

    def add_to_set(self, key: str, value: Any):
        res = self.storage.get(key, None)
        if res is None:
            res = set()
            res.add(value)
            self.storage[key] = res
            return
        self.check_if_valid(res, set)
        res.add(value)

    def get_set_list(self, key: str):
        res = self.storage.get(key, None)
        if res is None:
            return None
        self.check_if_valid(res, set)
        return list(res)

    """
    METHODS FOR NODE INIT
    """

    # -- for node container --
    def clear_node_init_containers(self):
        self.node_init_container.clear()

    def set_init_container(self, node_id: str, value):
        self.node_init_container[node_id] = value

    def get_init_container(self, node_id: str):
        res = self.node_init_container.get(node_id, None)
        from .node_init import NodeInitContainer  # avoid circular import

        self.check_if_valid(res, NodeInitContainer)
        return res

    def has_init_container(self, node_id: str) -> bool:
        return node_id in self.node_init_container.keys()

    # ------------------------

    # -- for node init function --
    def set_init_function(self, node_func, node_init_func):
        self.node_init_func[node_func] = node_init_func

    def get_init_function(self, node_func: Callable):
        res = self.node_init_func.get(node_func, None)
        from .node_init import NodeInit  # avoid circular import

        self.check_if_valid(res, NodeInit)
        return res

    def has_init_function(self, node_func) -> bool:
        return node_func in self.node_init_func.keys()

    # ----------------------------
