"""Configure nozzle layout command request, result, and implementation models."""
from __future__ import annotations
from pydantic import BaseModel
from typing import TYPE_CHECKING, Optional, Type, Tuple, Union
from typing_extensions import Literal

from .pipetting_common import (
    PipetteIdMixin,
)
from .command import (
    AbstractCommandWithPrivateResultImpl,
    BaseCommand,
    BaseCommandCreate,
)
from .configuring_common import (
    PipetteNozzleLayoutResultMixin,
)
from ..types import (EmptyNozzleLayoutConfiguration, SingleNozzleLayoutConfiguration, RowNozzleLayoutConfiguration, QuadrantNozzleLayoutConfiguration)

if TYPE_CHECKING:
    from ..execution import EquipmentHandler, TipHandler


ConfigureNozzleLayoutCommandType = Literal["configureNozzleLayout"]


class ConfigureNozzleLayoutParams(PipetteIdMixin):
    """Parameters required to configure the nozzle layout for a specific pipette."""

    configuration_params: Union[
        EmptyNozzleLayoutConfiguration,
        SingleNozzleLayoutConfiguration,
        RowNozzleLayoutConfiguration,
        QuadrantNozzleLayoutConfiguration,
    ]


class ConfigureNozzleLayoutPrivateResult(PipetteNozzleLayoutResultMixin):
    """Result sent to the store but not serialized."""

    pass


class ConfigureNozzleLayoutResult(BaseModel):
    """Result data from execution of an configureNozzleLayout command."""

    pass


class ConfigureNozzleLayoutImplementation(
    AbstractCommandWithPrivateResultImpl[
        ConfigureNozzleLayoutParams,
        ConfigureNozzleLayoutResult,
        ConfigureNozzleLayoutPrivateResult,
    ]
):
    """Configure for volume command implementation."""

    def __init__(
        self, equipment: EquipmentHandler, tip_handler: TipHandler, **kwargs: object
    ) -> None:
        self._equipment = equipment
        self._tip_handler = tip_handler

    async def execute(
        self, params: ConfigureNozzleLayoutParams
    ) -> Tuple[ConfigureNozzleLayoutResult, ConfigureNozzleLayoutPrivateResult]:
        """Check that requested pipette can support the requested nozzle layout."""

        # check if a tip is attached
        # move to tip handler
        # if self._core.has_tip():
        #     raise CommandPreconditionViolated(
        #         message=f"Cannot configure nozzle layout of {str(self)} while it has tips attached."
        #     )
        nozzle_params = await self._tip_handler.available_for_nozzle_layout(
            params.configuration_params.type.upper(), params
        )

        # style = params.configuration_style.upper()

        nozzle_map = await self._equipment.configure_nozzle_layout(
            pipette_id=params.pipetteId,
            **nozzle_params,
        )

        return ConfigureNozzleLayoutResult(), ConfigureNozzleLayoutPrivateResult(
            pipette_id=params.pipetteId,
            nozzle_map=nozzle_map,
        )


class ConfigureNozzleLayout(
    BaseCommand[ConfigureNozzleLayoutParams, ConfigureNozzleLayoutResult]
):
    """Configure nozzle layout command model."""

    commandType: ConfigureNozzleLayoutCommandType = "configureNozzleLayout"
    params: ConfigureNozzleLayoutParams
    result: Optional[ConfigureNozzleLayoutResult]

    _ImplementationCls: Type[
        ConfigureNozzleLayoutImplementation
    ] = ConfigureNozzleLayoutImplementation


class ConfigureNozzleLayoutCreate(BaseCommandCreate[ConfigureNozzleLayoutParams]):
    """Configure nozzle layout creation request model."""

    commandType: ConfigureNozzleLayoutCommandType = "configureNozzleLayout"
    params: ConfigureNozzleLayoutParams

    _CommandCls: Type[ConfigureNozzleLayout] = ConfigureNozzleLayout
