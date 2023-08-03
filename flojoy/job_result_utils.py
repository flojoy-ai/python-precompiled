from .flojoy_instruction import FLOJOY_INSTRUCTION
from .data_container import DataContainer
from .dao import Dao
from typing import Any, cast

__all__ = ["get_job_result", "get_next_directions", "get_next_nodes", "get_job_result"]


def is_flow_controled(result):
    if (
        FLOJOY_INSTRUCTION.FLOW_TO_DIRECTIONS in result
        or FLOJOY_INSTRUCTION.FLOW_TO_NODES in result
    ):
        return True
    return False


def get_next_directions(result):
    direction = None
    if result is None:
        return direction
    if not result.get(FLOJOY_INSTRUCTION.FLOW_TO_DIRECTIONS):
        for value in result.values():
            if isinstance(value, dict) and value.get(
                FLOJOY_INSTRUCTION.FLOW_TO_DIRECTIONS
            ):
                direction = cast(
                    list, value[FLOJOY_INSTRUCTION.FLOW_TO_DIRECTIONS]
                )
                break
    else:
        direction = result[FLOJOY_INSTRUCTION.FLOW_TO_DIRECTIONS]
    return direction


def get_next_nodes(result) -> list:
    if result is None:
        return []
    return cast(list, result.get(FLOJOY_INSTRUCTION.FLOW_TO_NODES, []))


def get_dc_from_result(
    result
):
    if not result:
        return None
    if isinstance(result, DataContainer):
        return result
    if result.get(FLOJOY_INSTRUCTION.RESULT_FIELD):
        return result[result[FLOJOY_INSTRUCTION.RESULT_FIELD]]
    return result["data"]


def get_job_result(job_id: str):
    try:
        job_result = Dao.get_instance().get_job_result(job_id)
        result = get_dc_from_result(job_result)
        return result
    except Exception:
        return None


def get_text_blob_from_dc(dc: DataContainer):
    if dc.type == "text_blob":
        return dc.text_blob
    elif dc.type == "bytes":
        return dc.b.decode("utf-8")
    else:
        return None
