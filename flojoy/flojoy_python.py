from flojoy.node_init import NodeInitService
from typing import Callable, Any, Optional
from .job_result_utils import get_dc_from_result
from .config import logger
from .parameter_types import format_param_value
from .job_service import JobService

__all__ = ["flojoy", "DefaultParams"]


def fetch_inputs(previous_jobs: list):
    """
    Queries for job results

    Parameters
    ----------
    previous_jobs : list of jobs that directly precede this node.
    Each item representing a job contains `job_id` and `input_name`.
    `input_name` is the port where the previous job with `job_id` connects to.

    Returns
    -------
    inputs : list of DataContainer objects
    """
    dict_inputs = dict()

    try:
        for prev_job in previous_jobs:
            prev_job_id = prev_job.get("job_id")
            input_name = prev_job.get("input_name", "")
            multiple = prev_job.get("multiple", False)
            edge = prev_job.get("edge", "")

            logger(
                "fetching input from prev job id:",
                prev_job_id,
                " for input:",
                input_name,
                "edge: ",
                edge,
            )

            job_result = JobService().get_job_result(prev_job_id)
            if not job_result:
                raise ValueError(
                    "Tried to get job result from %s but it was None" % prev_job_id
                )

            result = (
                get_dc_from_result(job_result[edge])
                if edge != "default"
                else get_dc_from_result(job_result)
            )
            if result is not None:
                logger("got job result from %s" % prev_job_id)
                if multiple:
                    if input_name not in dict_inputs:
                        dict_inputs[input_name] = [result]
                    else:
                        dict_inputs[input_name].append(result)
                else:
                    dict_inputs[input_name] = result

    except Exception as e:
        logger("error occured while fetching inputs", e)

    return dict_inputs


class DefaultParams:
    def __init__(
        self, node_id: str, job_id: str, jobset_id: str, node_type: str
    ) -> None:
        self.node_id = node_id
        self.job_id = job_id
        self.jobset_id = jobset_id
        self.node_type = node_type


def flojoy(
    original_function = None,
    *,
    node_type: Optional[str] = None,
    deps = None,
    inject_node_metadata: bool = False,
):
    """
    Decorator to turn Python functions with numerical return
    values into Flojoy nodes.

    @flojoy is intended to eliminate boilerplate in connecting
    Python scripts as visual nodes

    Into whatever function it wraps, @flojoy injects
    1. the last node's input as list of DataContainer object
    2. parameters for that function (either set by the user or default)

    Parameters
    ----------
    `func`: Python function that returns DataContainer object

    Returns
    -------
    A dict containing DataContainer object

    Usage Example
    -------------
    ```
    @flojoy
    def SINE(dc_inputs:list[DataContainer], params:dict[str, Any]):

        logger('params passed to SINE', params)

        dc_input = dc_inputs[0]

        output = DataContainer(
            x=dc_input.x,
            y=np.sin(dc_input.x)
        )
        return output
    ```

    ## equivalent to: decorated_sine = flojoy(SINE)
    ```
    pj_ids = [123, 456]
    logger(SINE(previous_job_ids = pj_ids, mock = True))
    ```
    """

    def decorator(func):
        def wrapper(
            node_id: str,
            job_id: str,
            jobset_id: str,
            previous_jobs: list = [],
            function_parameters: set = set(),
            ctrls = None,
        ):
            FN = func.__name__

            logger("previous jobs:", previous_jobs)
            # Get command parameters set by the user through the control panel
            func_params = {}
            if ctrls is not None:
                for _, input in ctrls.items():
                    param = input["param"]
                    value = input["value"]
                    func_params[param] = format_param_value(value, input["type"])
            func_params["type"] = "default"

            logger(
                "executing node_id:",
                node_id,
                "previous_jobs:",
                previous_jobs,
            )
            dict_inputs = fetch_inputs(previous_jobs)

            # constructing the inputs
            logger("constructing inputs for %s" % func.__name__)
            args = {}

            args = dict_inputs

            for param, value in func_params.items():
                if param in function_parameters:
                    args[param] = value
            if inject_node_metadata:
                args["default_params"] = DefaultParams(
                    job_id=job_id,
                    node_id=node_id,
                    jobset_id=jobset_id,
                    node_type="default",
                )

            logger(node_id, " params: ", args.keys())

            # check if node has an init container and if so, inject it
            if NodeInitService().has_init_store(node_id):
                args["init_container"] = NodeInitService().get_init_store(node_id)

            ##########################
            # calling the node function
            ##########################
            dc_obj = func(**args)  # DataContainer object from node
            ##########################
            # end calling the node function
            ##########################

            # # some special nodes like LOOP return dict instead of `DataContainer`
            # if isinstance(dc_obj, DataContainer):
            #     dc_obj.validate()  # Validate returned DataContainer object
            # else:
            #     for value in dc_obj.values():
            #         if isinstance(value, DataContainer):
            #             value.validate()
            JobService().post_job_result(
                job_id, dc_obj
            )  # post result to the job service before sending result to socket
            return dc_obj

        return wrapper

    if original_function:
        return decorator(original_function)

    return decorator

