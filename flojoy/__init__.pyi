from typing import Optional, Any
from .data_container import *
from .flojoy_python import *
from .job_result_builder import *
from .flojoy_instruction import *
from .job_result_utils import *
from .utils import *
from .parameter_types import *
from .small_memory import *
from .job_service import *
from .node_init import *
from .data_container import *
from .config import *


def flojoy(
    original_function = None,
    *,
    node_type: Optional[str] = None,
    deps: Optional[dict[str, str]] = None,
    inject_node_metadata: bool = False,
) -> Callable[..., DataContainer | dict[str, Any]]: ...
