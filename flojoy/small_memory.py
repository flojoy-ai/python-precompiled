# import os, sys
from typing import Any
from .dao import Dao

class SmallMemory:
    """
    SmallMemory - available during jobset execution - intended to be used ONLY inside node functions
    """

    tracing_key = "ALL_MEMORY_KEYS"
    dao = Dao.get_instance()

    def clear_memory(self):
        self.dao.clear_small_memory()

    def write_to_memory(self, job_id: str, key: str, value: Any):
        memory_key = "%s-%s" % (job_id, key)
        value_type_key = "%s_value_type_key" % memory_key
        meta_data = {}
        s = str(type(value))
        v_type = s.split("'")[1]
        if v_type == "numpy.ndarray":
            array_dtype = str(value.dtype)
            meta_data["type"] = "np_array"
            meta_data["d_type"] = array_dtype
            meta_data["dimensions"] = value.shape
            self.dao.set_obj(value_type_key, meta_data)
            self.dao.set_np_array(memory_key, value)
        elif v_type == "str" or v_type == "numpy.float64":
            meta_data["type"] = "string"
            self.dao.set_obj(value_type_key, meta_data)
            self.dao.set_str(memory_key, value)
        elif v_type == "dict":
            meta_data["type"] = "dict"
            self.dao.set_obj(value_type_key, meta_data)
            self.dao.set_obj(memory_key, value)
        else:
            raise ValueError(
                "SmallMemory currently does not support '%s' type data!" % v_type
            )

    def read_memory(self, job_id: str, key: str):
        """
        Reads object stored in internal DB by the given key. The memory is job specific.
        """
        memory_key = "%s-%s" % (job_id, key)
        value_type_key = "%s_value_type_key" % memory_key
        meta_data = self.dao.get_obj(value_type_key)
        if not meta_data:
            return None
        meta_type = meta_data.get("type")
        if meta_type == "string":
            return self.dao.get_str(memory_key)
        elif meta_type == "dict":
            return self.dao.get_obj(memory_key)
        elif meta_type == "np_array":
            return self.dao.get_np_array(memory_key, meta_data)
        else:
            return None

    def delete_object(self, job_id: str, key: str):
        """
        Removes object stored in internal DB by the given key. The memory is job specific.
        """
        memory_key = "%s-%s" % (job_id, key)
        return self.dao.delete_object(memory_key)
