from .data_container import DataContainer
from ulab import numpy as np
from typing import Union
from .flojoy_instruction import FLOJOY_INSTRUCTION


class JobResultBuilder:
    instructions = None

    def __init__(self) -> None:
        self.data = self.get_default_data()

    def _add_instructions(self, instruction):
        self.instructions = self.instructions if self.instructions is not None else {}
        self.instructions = {
            **self.instructions,
            **instruction,
        }

    def from_inputs(self, inputs: list):
        # if no inputs were provided, construct fake output
        if len(inputs) == 0:
            self.data = self.get_default_data()
        else:
            self.data = inputs[0]

        return self

    def from_data(self, data: DataContainer):
        self.data = data
        return self

    def flow_to_nodes(self, nodes: list):
        if nodes.__len__() > 0:
            self._add_instructions({FLOJOY_INSTRUCTION.FLOW_TO_NODES: nodes})
        return self

    def flow_to_directions(self, directions: list):
        if directions.__len__() > 0:
            self._add_instructions({FLOJOY_INSTRUCTION.FLOW_TO_DIRECTIONS: directions})
        return self

    def flow_by_flag(
        self, flag: bool, true_direction: list, false_direction: list
    ):
        self._add_instructions(
            {
                FLOJOY_INSTRUCTION.FLOW_TO_DIRECTIONS: true_direction
                if flag
                else false_direction
            }
        )
        return self

    def build(self):
        result = self.data
        if self.instructions:
            result = {
                # instructions to job scheduler (watch.py)
                **self.instructions,
                # instruction to fetch_input method in flojoy.py
                FLOJOY_INSTRUCTION.RESULT_FIELD: "data",
                "data": result,
            }
        return result

    def get_default_data(self) -> DataContainer:
        x = np.arange(0, 1000, 1)  # type:ignore
        y = np.ones_like(x)
        return DataContainer(x=x, y=y)
