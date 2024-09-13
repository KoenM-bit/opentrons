""" opentrons_shared_data.labware.types: types for labware defs

types in this file by and large require the use of typing_extensions.
this module shouldn't be imported unless typing.TYPE_CHECKING is true.
"""
from typing import Dict, List, NewType, Union, Optional, Any
from typing_extensions import Literal, TypedDict, NotRequired, TypeGuard


LabwareUri = NewType("LabwareUri", str)

LabwareDisplayCategory = Union[
    Literal["tipRack"],
    Literal["tubeRack"],
    Literal["reservoir"],
    Literal["trash"],
    Literal["wellPlate"],
    Literal["aluminumBlock"],
    Literal["adapter"],
    Literal["other"],
]

LabwareFormat = Union[
    Literal["96Standard"],
    Literal["384Standard"],
    Literal["trough"],
    Literal["irregular"],
    Literal["trash"],
]

LabwareRoles = Union[
    Literal["labware"],
    Literal["fixture"],
    Literal["adapter"],
    Literal["maintenance"],
]

Circular = Literal["circular"]
Rectangular = Literal["rectangular"]
Spherical = Literal["spherical"]
WellShape = Union[Circular, Rectangular]


class NamedOffset(TypedDict):
    x: float
    y: float
    z: float


class GripperOffsets(TypedDict):
    pickUpOffset: NamedOffset
    dropOffset: NamedOffset


class LabwareParameters(TypedDict, total=False):
    format: LabwareFormat
    isTiprack: bool
    loadName: str
    isMagneticModuleCompatible: bool
    quirks: List[str]
    tipLength: float
    tipOverlap: float
    magneticModuleEngageHeight: float


class LabwareBrandData(TypedDict, total=False):
    brand: str
    brandId: List[str]
    links: List[str]


class LabwareMetadata(TypedDict, total=False):
    displayName: str
    displayCategory: LabwareDisplayCategory
    displayVolumeUnits: Union[Literal["µL"], Literal["mL"], Literal["L"]]
    tags: List[str]


class LabwareDimensions(TypedDict):
    yDimension: float
    zDimension: float
    xDimension: float


class CircularWellDefinition(TypedDict):
    shape: Circular
    depth: float
    totalLiquidVolume: float
    x: float
    y: float
    z: float
    diameter: float
    geometryDefinitionId: NotRequired[str]


class RectangularWellDefinition(TypedDict):
    shape: Rectangular
    depth: float
    totalLiquidVolume: float
    x: float
    y: float
    z: float
    xDimension: float
    yDimension: float
    geometryDefinitionId: NotRequired[str]


WellDefinition = Union[CircularWellDefinition, RectangularWellDefinition]


class WellGroupMetadata(TypedDict, total=False):
    displayName: str
    displayCategory: LabwareDisplayCategory
    wellBottomShape: Union[Literal["flat"], Literal["u"], Literal["v"]]


class WellGroup(TypedDict, total=False):
    wells: List[str]
    metadata: WellGroupMetadata
    brand: LabwareBrandData


class SphericalSegment(TypedDict):
    shape: Spherical
    radiusOfCurvature: float
    depth: float


class RectangularBoundedSection(TypedDict):
    shape: Rectangular
    xDimension: float
    yDimension: float
    topHeight: float


class CircularBoundedSection(TypedDict):
    shape: Circular
    diameter: float
    topHeight: float


def is_circular_frusta_list(
    items: List[Any],
) -> TypeGuard[List[CircularBoundedSection]]:
    return all(item.shape == "circular" for item in items)


def is_rectangular_frusta_list(
    items: List[Any],
) -> TypeGuard[List[RectangularBoundedSection]]:
    return all(item.shape == "rectangular" for item in items)


class InnerWellGeometry(TypedDict):
    frusta: Union[List[CircularBoundedSection], List[RectangularBoundedSection]]
    bottomShape: Optional[SphericalSegment]


class LabwareDefinition(TypedDict):
    schemaVersion: Literal[2]
    version: int
    namespace: str
    metadata: LabwareMetadata
    brand: LabwareBrandData
    parameters: LabwareParameters
    cornerOffsetFromSlot: NamedOffset
    ordering: List[List[str]]
    dimensions: LabwareDimensions
    wells: Dict[str, WellDefinition]
    groups: List[WellGroup]
    stackingOffsetWithLabware: NotRequired[Dict[str, NamedOffset]]
    stackingOffsetWithModule: NotRequired[Dict[str, NamedOffset]]
    allowedRoles: NotRequired[List[LabwareRoles]]
    gripperOffsets: NotRequired[Dict[str, GripperOffsets]]
    gripForce: NotRequired[float]
    gripHeightFromLabwareBottom: NotRequired[float]
    innerLabwareGeometry: NotRequired[Dict[str, InnerWellGeometry]]
